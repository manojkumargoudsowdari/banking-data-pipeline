import argparse
import csv
import logging
import sys
from datetime import date, datetime
from pathlib import Path

import duckdb

CURATED_MODELS = [
    "dim_customer",
    "dim_account",
    "dim_branch",
    "dim_product",
    "fact_transaction",
    "fact_customer_risk_score",
    "fact_daily_account_balance",
]

STANDARDIZED_TABLES = [
    "customers",
    "accounts",
    "transactions",
    "branches",
    "products",
    "customer_risk_scores",
    "reference_codes",
]

EXPECTED_RESULT_COLUMNS = [
    "check_category",
    "check_name",
    "table_name",
    "column_name",
    "severity",
    "failed_record_count",
    "status",
    "details",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run DuckDB SQL validation checks directly against Parquet data."
    )
    parser.add_argument("--load-date", required=True, help="Load date in YYYY-MM-DD format.")
    parser.add_argument("--curated-dir", default="data/curated")
    parser.add_argument("--standardized-dir", default="data/standardized")
    parser.add_argument("--sql-dir", default="sql/validation")
    parser.add_argument("--output-dir", default="data/dq_results/sql")
    parser.add_argument("--log-dir", default="logs/sql")
    parser.add_argument(
        "--checks",
        nargs="+",
        help="Optional SQL filenames to run. Defaults to all SQL files in --sql-dir.",
    )
    return parser.parse_args()


def validate_load_date(load_date):
    try:
        parsed_date = datetime.strptime(load_date, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("--load-date must use YYYY-MM-DD format.") from exc
    if parsed_date.isoformat() != load_date:
        raise ValueError("--load-date must use YYYY-MM-DD format.")
    return parsed_date.isoformat()


def configure_logging(log_dir):
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_path / f"sql_validation_{run_timestamp}.log"

    logger = logging.getLogger("sql_validation")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger, run_timestamp, log_file


def select_checks(sql_dir, requested_checks):
    sql_path = Path(sql_dir)
    if not sql_path.is_dir():
        raise ValueError(f"SQL directory not found: {sql_path}")

    if requested_checks:
        check_paths = []
        for filename in requested_checks:
            if Path(filename).name != filename or not filename.lower().endswith(".sql"):
                raise ValueError(f"Invalid SQL check filename: {filename}")
            check_path = sql_path / filename
            if not check_path.is_file():
                raise ValueError(f"SQL check file not found: {check_path}")
            check_paths.append(check_path)
        return check_paths

    check_paths = sorted(sql_path.glob("*.sql"))
    if not check_paths:
        raise ValueError(f"No SQL check files found in: {sql_path}")
    return check_paths


def parquet_source(base_dir, entity_name, load_date):
    parquet_path = (
        Path(base_dir)
        / entity_name
        / f"load_date={load_date}"
        / f"{entity_name}.parquet"
    )
    if parquet_path.is_file():
        return parquet_path.resolve().as_posix()
    if parquet_path.is_dir():
        part_files = list(parquet_path.rglob("*.parquet"))
        if not part_files:
            raise FileNotFoundError(f"No Parquet part files found under: {parquet_path}")
        return f"{parquet_path.resolve().as_posix()}/**/*.parquet"
    raise FileNotFoundError(f"Parquet input not found: {parquet_path}")


def sql_literal(value):
    return value.replace("'", "''")


def create_parquet_view(connection, view_name, parquet_path):
    path_literal = sql_literal(parquet_path)
    connection.execute(
        f"""
        CREATE OR REPLACE VIEW {view_name} AS
        SELECT *
        FROM read_parquet(
            '{path_literal}',
            hive_partitioning = false,
            union_by_name = true
        )
        """
    )


def create_all_views(connection, curated_dir, standardized_dir, load_date, logger):
    for model_name in CURATED_MODELS:
        source = parquet_source(curated_dir, model_name, load_date)
        create_parquet_view(connection, model_name, source)
        logger.info("Created view=%s parquet_source=%s", model_name, source)

    for table_name in STANDARDIZED_TABLES:
        view_name = f"std_{table_name}"
        source = parquet_source(standardized_dir, table_name, load_date)
        create_parquet_view(connection, view_name, source)
        logger.info("Created view=%s parquet_source=%s", view_name, source)


def validate_result_columns(result_df, check_name):
    actual_columns = [column.lower() for column in result_df.columns]
    if actual_columns != EXPECTED_RESULT_COLUMNS:
        raise ValueError(
            f"{check_name} returned columns {actual_columns}; "
            f"expected {EXPECTED_RESULT_COLUMNS}"
        )


def write_summary(summary_rows, log_dir, run_timestamp):
    summary_path = Path(log_dir) / f"sql_validation_summary_{run_timestamp}.csv"
    fieldnames = [
        "check_file",
        "status",
        "result_row_count",
        "failed_check_count",
        "output_path",
        "error_message",
    ]
    with summary_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)
    return summary_path


def main():
    args = parse_args()
    try:
        load_date = validate_load_date(args.load_date)
        check_paths = select_checks(args.sql_dir, args.checks)
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    logger, run_timestamp, log_file = configure_logging(args.log_dir)
    result_dir = Path(args.output_dir) / f"load_date={load_date}"
    result_dir.mkdir(parents=True, exist_ok=True)
    summary_rows = []
    connection = None

    logger.info("DuckDB SQL validation started.")
    logger.info("load_date=%s", load_date)
    logger.info("checks=%s", ",".join(path.name for path in check_paths))
    logger.info("result_dir=%s", result_dir)
    logger.info("log_file=%s", log_file)

    try:
        connection = duckdb.connect(database=":memory:")
        create_all_views(
            connection,
            args.curated_dir,
            args.standardized_dir,
            load_date,
            logger,
        )

        for check_path in check_paths:
            output_path = result_dir / f"{check_path.stem}_results.csv"
            logger.info("Starting check_file=%s", check_path.name)
            try:
                sql_text = check_path.read_text(encoding="utf-8")
                result_df = connection.execute(sql_text).fetchdf()
                validate_result_columns(result_df, check_path.name)
                result_df.to_csv(output_path, index=False)

                failed_check_count = int(
                    result_df["status"].astype(str).str.upper().eq("FAIL").sum()
                )
                logger.info("check_file=%s result_row_count=%s", check_path.name, len(result_df))
                logger.info(
                    "check_file=%s failed_check_count=%s",
                    check_path.name,
                    failed_check_count,
                )
                logger.info("check_file=%s output_path=%s", check_path.name, output_path)
                logger.info("check_file=%s execution_status=SUCCESS", check_path.name)

                summary_rows.append(
                    {
                        "check_file": check_path.name,
                        "status": "SUCCESS",
                        "result_row_count": len(result_df),
                        "failed_check_count": failed_check_count,
                        "output_path": str(output_path),
                        "error_message": "",
                    }
                )
            except Exception as exc:
                logger.exception(
                    "check_file=%s execution_status=FAILED error=%s",
                    check_path.name,
                    exc,
                )
                summary_rows.append(
                    {
                        "check_file": check_path.name,
                        "status": "FAILED",
                        "result_row_count": 0,
                        "failed_check_count": 0,
                        "output_path": str(output_path),
                        "error_message": str(exc),
                    }
                )
    except Exception as exc:
        logger.exception("SQL validation runner failed: %s", exc)
        summary_rows.append(
            {
                "check_file": "__runner__",
                "status": "FAILED",
                "result_row_count": 0,
                "failed_check_count": 0,
                "output_path": "",
                "error_message": str(exc),
            }
        )
    finally:
        if connection is not None:
            connection.close()

    summary_path = write_summary(summary_rows, args.log_dir, run_timestamp)
    execution_failures = [row for row in summary_rows if row["status"] == "FAILED"]
    total_dq_failures = sum(int(row["failed_check_count"]) for row in summary_rows)

    logger.info("Final summary:")
    for row in summary_rows:
        logger.info(
            "check_file=%s status=%s result_row_count=%s failed_check_count=%s output_path=%s",
            row["check_file"],
            row["status"],
            row["result_row_count"],
            row["failed_check_count"],
            row["output_path"],
        )
    logger.info("total_dq_failed_checks=%s", total_dq_failures)
    logger.info("summary_csv=%s", summary_path)

    if execution_failures:
        logger.error(
            "final_run_result=FAILED execution_failure_count=%s",
            len(execution_failures),
        )
        return 1

    logger.info("final_run_result=SUCCESS")
    logger.info("DuckDB SQL validation completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
