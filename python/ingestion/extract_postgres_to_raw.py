import argparse
import csv
import logging
import sys
from datetime import date, datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db_connection import get_postgres_engine

SOURCE_TABLES = [
    "branches",
    "products",
    "reference_codes",
    "customers",
    "accounts",
    "transactions",
    "customer_risk_scores",
    "data_quality_rules",
    "stewardship_issues",
    "source_to_target_mappings",
]

PRIMARY_KEYS = {
    "branches": "branch_id",
    "products": "product_id",
    "reference_codes": "reference_code_id",
    "customers": "customer_id",
    "accounts": "account_id",
    "transactions": "transaction_id",
    "customer_risk_scores": "risk_score_id",
    "data_quality_rules": "dq_rule_id",
    "stewardship_issues": "issue_id",
    "source_to_target_mappings": "mapping_id",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract whitelisted PostgreSQL source tables to raw Parquet files."
    )
    parser.add_argument(
        "--load-date",
        default=date.today().isoformat(),
        help="Load date partition in YYYY-MM-DD format. Defaults to today.",
    )
    parser.add_argument(
        "--output-dir",
        default="data/raw",
        help="Base output directory for raw Parquet files.",
    )
    parser.add_argument(
        "--log-dir",
        default="logs/ingestion",
        help="Directory for ingestion runtime logs and summary files.",
    )
    parser.add_argument(
        "--tables",
        default=",".join(SOURCE_TABLES),
        help="Comma-separated source table list. Defaults to all whitelisted tables.",
    )
    return parser.parse_args()


def validate_load_date(load_date):
    try:
        return date.fromisoformat(load_date).isoformat()
    except ValueError as exc:
        raise ValueError("--load-date must use YYYY-MM-DD format.") from exc


def parse_tables(tables_arg):
    requested_tables = [table.strip() for table in tables_arg.split(",") if table.strip()]
    if not requested_tables:
        raise ValueError("At least one table must be requested.")

    invalid_tables = [table for table in requested_tables if table not in SOURCE_TABLES]
    if invalid_tables:
        allowed = ", ".join(SOURCE_TABLES)
        invalid = ", ".join(invalid_tables)
        raise ValueError(f"Invalid table name(s): {invalid}. Allowed tables: {allowed}")

    return requested_tables


def configure_logging(log_dir):
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_path / f"postgres_to_raw_{run_timestamp}.log"

    logger = logging.getLogger("postgres_to_raw")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger, log_file, run_timestamp


def extract_table(engine, table_name, output_dir, load_date):
    primary_key = PRIMARY_KEYS[table_name]
    query = text(f'SELECT * FROM public."{table_name}" ORDER BY "{primary_key}"')

    with engine.connect() as conn:
        df = pd.read_sql_query(query, conn)

    table_output_dir = Path(output_dir) / table_name / f"load_date={load_date}"
    table_output_dir.mkdir(parents=True, exist_ok=True)
    output_path = table_output_dir / f"{table_name}.parquet"
    df.to_parquet(output_path, index=False, engine="pyarrow")

    return len(df), output_path


def write_summary_csv(summary_rows, log_dir, run_timestamp):
    summary_path = Path(log_dir) / f"postgres_to_raw_summary_{run_timestamp}.csv"
    fieldnames = ["table_name", "row_count", "output_path", "status", "error"]

    with summary_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)

    return summary_path


def main():
    args = parse_args()

    try:
        load_date = validate_load_date(args.load_date)
        selected_tables = parse_tables(args.tables)
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    logger, log_file, run_timestamp = configure_logging(args.log_dir)
    summary_rows = []

    logger.info("PostgreSQL to raw Parquet extraction started.")
    logger.info("load_date=%s", load_date)
    logger.info("selected_tables=%s", ",".join(selected_tables))
    logger.info("output_dir=%s", args.output_dir)
    logger.info("log_file=%s", log_file)

    try:
        engine = get_postgres_engine()
    except Exception as exc:
        logger.error("Failed to create PostgreSQL engine: %s", exc)
        summary_rows.append(
            {
                "table_name": "__connection__",
                "row_count": 0,
                "output_path": "",
                "status": "FAILED",
                "error": str(exc),
            }
        )
        summary_path = write_summary_csv(summary_rows, args.log_dir, run_timestamp)
        logger.info("summary_csv=%s", summary_path)
        return 1

    for table_name in selected_tables:
        logger.info("Starting extraction for table=%s", table_name)
        try:
            row_count, output_path = extract_table(engine, table_name, args.output_dir, load_date)
            logger.info("table=%s row_count=%s", table_name, row_count)
            logger.info("table=%s output_path=%s", table_name, output_path)
            logger.info("table=%s status=SUCCESS", table_name)
            summary_rows.append(
                {
                    "table_name": table_name,
                    "row_count": row_count,
                    "output_path": str(output_path),
                    "status": "SUCCESS",
                    "error": "",
                }
            )
        except Exception as exc:
            logger.exception("table=%s status=FAILED error=%s", table_name, exc)
            summary_rows.append(
                {
                    "table_name": table_name,
                    "row_count": 0,
                    "output_path": "",
                    "status": "FAILED",
                    "error": str(exc),
                }
            )
            summary_path = write_summary_csv(summary_rows, args.log_dir, run_timestamp)
            logger.info("summary_csv=%s", summary_path)
            logger.error("Extraction failed.")
            return 1

    summary_path = write_summary_csv(summary_rows, args.log_dir, run_timestamp)

    logger.info("Final summary:")
    for row in summary_rows:
        logger.info(
            "table=%s row_count=%s status=%s output_path=%s",
            row["table_name"],
            row["row_count"],
            row["status"],
            row["output_path"],
        )
    logger.info("summary_csv=%s", summary_path)
    logger.info("PostgreSQL to raw Parquet extraction completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
