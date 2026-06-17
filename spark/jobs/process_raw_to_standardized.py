import argparse
import csv
import logging
import re
import shutil
import sys
from datetime import date, datetime
from pathlib import Path

import pyarrow.parquet as pq
from pyspark.sql import functions as F
from pyspark.sql.types import StringType

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from spark.utils.spark_session import create_spark_session

APPROVED_TABLES = [
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

UPPERCASE_COLUMN_TOKENS = ["status", "type", "code", "category"]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Process raw PostgreSQL Parquet extracts into standardized Parquet outputs."
    )
    parser.add_argument("--load-date", required=True, help="Load date partition in YYYY-MM-DD format.")
    parser.add_argument("--input-dir", default="data/raw", help="Base raw input directory.")
    parser.add_argument(
        "--output-dir",
        default="data/standardized",
        help="Base standardized output directory.",
    )
    parser.add_argument("--log-dir", default="logs/spark", help="Directory for Spark runtime logs.")
    parser.add_argument(
        "--tables",
        help="Optional comma-separated table list. Defaults to all approved tables.",
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


def parse_tables(tables_arg):
    if not tables_arg:
        return APPROVED_TABLES

    requested_tables = [table.strip() for table in tables_arg.split(",") if table.strip()]
    if not requested_tables:
        raise ValueError("At least one table must be requested.")

    invalid_tables = [table for table in requested_tables if table not in APPROVED_TABLES]
    if invalid_tables:
        allowed = ", ".join(APPROVED_TABLES)
        invalid = ", ".join(invalid_tables)
        raise ValueError(f"Invalid table name(s): {invalid}. Allowed tables: {allowed}")

    return requested_tables


def configure_logging(log_dir):
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_path / f"raw_to_standardized_{run_timestamp}.log"

    logger = logging.getLogger("raw_to_standardized")
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


def to_snake_case(column_name):
    value = re.sub(r"[^0-9a-zA-Z]+", "_", column_name.strip())
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    value = re.sub(r"_+", "_", value).strip("_").lower()
    return value


def make_unique_column_names(column_names):
    seen = {}
    unique_names = []
    for column_name in column_names:
        base_name = to_snake_case(column_name)
        count = seen.get(base_name, 0)
        unique_name = base_name if count == 0 else f"{base_name}_{count + 1}"
        seen[base_name] = count + 1
        unique_names.append(unique_name)
    return unique_names


def standardize_dataframe(df, table_name, load_date):
    standardized_columns = make_unique_column_names(df.columns)
    df = df.toDF(*standardized_columns)

    string_columns = [
        field.name for field in df.schema.fields if isinstance(field.dataType, StringType)
    ]

    for column_name in string_columns:
        cleaned_col = F.trim(F.col(column_name))
        cleaned_col = F.when(F.length(cleaned_col) == 0, F.lit(None)).otherwise(cleaned_col)

        if "email" in column_name:
            cleaned_col = F.lower(cleaned_col)
        elif column_name == "source_system" or any(
            token in column_name for token in UPPERCASE_COLUMN_TOKENS
        ):
            cleaned_col = F.upper(cleaned_col)

        df = df.withColumn(column_name, cleaned_col)

    return (
        df.withColumn("source_table", F.lit(table_name))
        .withColumn("source_load_date", F.lit(load_date).cast("date"))
        .withColumn("standardized_load_date", F.current_date())
        .withColumn("standardized_at_utc", F.current_timestamp())
    )


def write_single_parquet(df, output_path):
    final_path = Path(output_path)
    partition_dir = final_path.parent
    if final_path.exists():
        if final_path.is_dir():
            shutil.rmtree(final_path)
        else:
            final_path.unlink()

    partition_dir.mkdir(parents=True, exist_ok=True)
    pandas_df = df.toPandas()
    pandas_df.to_parquet(
        final_path,
        index=False,
        engine="pyarrow",
        coerce_timestamps="us",
        allow_truncated_timestamps=True,
    )


def read_raw_parquet(spark, input_path, temp_dir):
    compatible_dir = Path(temp_dir)
    compatible_file = compatible_dir / "spark_compatible.parquet"
    if compatible_dir.exists():
        shutil.rmtree(compatible_dir)
    compatible_dir.mkdir(parents=True, exist_ok=True)

    arrow_table = pq.ParquetFile(input_path).read()
    pq.write_table(
        arrow_table,
        compatible_file,
        coerce_timestamps="us",
        allow_truncated_timestamps=True,
    )
    return spark.read.parquet(str(compatible_file)), compatible_dir


def process_table(spark, table_name, load_date, input_dir, output_dir):
    input_path = Path(input_dir) / table_name / f"load_date={load_date}" / f"{table_name}.parquet"
    output_path = (
        Path(output_dir) / table_name / f"load_date={load_date}" / f"{table_name}.parquet"
    )
    read_temp_dir = output_path.parent / f"_{table_name}_read_tmp"

    if not input_path.exists():
        raise FileNotFoundError(f"Raw input not found: {input_path}")

    read_temp_path = None
    try:
        raw_df, read_temp_path = read_raw_parquet(spark, input_path, read_temp_dir)
        raw_row_count = raw_df.count()

        standardized_df = standardize_dataframe(raw_df, table_name, load_date)
        write_single_parquet(standardized_df, output_path)

        standardized_row_count = pq.ParquetFile(output_path).metadata.num_rows

        return raw_row_count, standardized_row_count, input_path, output_path
    finally:
        if read_temp_path and Path(read_temp_path).exists():
            shutil.rmtree(read_temp_path)


def write_summary_csv(summary_rows, log_dir, run_timestamp):
    summary_path = Path(log_dir) / f"raw_to_standardized_summary_{run_timestamp}.csv"
    fieldnames = [
        "table_name",
        "status",
        "raw_row_count",
        "standardized_row_count",
        "input_path",
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
        selected_tables = parse_tables(args.tables)
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    logger, run_timestamp, log_file = configure_logging(args.log_dir)
    summary_rows = []
    spark = None

    logger.info("Raw to standardized Spark processing started.")
    logger.info("load_date=%s", load_date)
    logger.info("selected_tables=%s", ",".join(selected_tables))
    logger.info("input_dir=%s", args.input_dir)
    logger.info("output_dir=%s", args.output_dir)
    logger.info("log_file=%s", log_file)

    try:
        spark = create_spark_session()

        for table_name in selected_tables:
            logger.info("Starting table=%s", table_name)
            try:
                raw_count, standardized_count, input_path, output_path = process_table(
                    spark=spark,
                    table_name=table_name,
                    load_date=load_date,
                    input_dir=args.input_dir,
                    output_dir=args.output_dir,
                )
                logger.info("table=%s raw_row_count=%s", table_name, raw_count)
                logger.info("table=%s standardized_row_count=%s", table_name, standardized_count)
                logger.info("table=%s input_path=%s", table_name, input_path)
                logger.info("table=%s output_path=%s", table_name, output_path)

                if raw_count == standardized_count:
                    status = "SUCCESS"
                    error_message = ""
                    logger.info("table=%s row_count_match=TRUE", table_name)
                else:
                    status = "FAILED"
                    error_message = (
                        f"Row count mismatch: raw={raw_count}, standardized={standardized_count}"
                    )
                    logger.error("table=%s row_count_match=FALSE %s", table_name, error_message)

                summary_rows.append(
                    {
                        "table_name": table_name,
                        "status": status,
                        "raw_row_count": raw_count,
                        "standardized_row_count": standardized_count,
                        "input_path": str(input_path),
                        "output_path": str(output_path),
                        "error_message": error_message,
                    }
                )
                logger.info("table=%s status=%s", table_name, status)

            except Exception as exc:
                logger.exception("table=%s status=FAILED error=%s", table_name, exc)
                summary_rows.append(
                    {
                        "table_name": table_name,
                        "status": "FAILED",
                        "raw_row_count": 0,
                        "standardized_row_count": 0,
                        "input_path": str(
                            Path(args.input_dir)
                            / table_name
                            / f"load_date={load_date}"
                            / f"{table_name}.parquet"
                        ),
                        "output_path": str(
                            Path(args.output_dir)
                            / table_name
                            / f"load_date={load_date}"
                            / f"{table_name}.parquet"
                        ),
                        "error_message": str(exc),
                    }
                )

    finally:
        if spark is not None:
            spark.stop()

    summary_path = write_summary_csv(summary_rows, args.log_dir, run_timestamp)
    failed_rows = [row for row in summary_rows if row["status"] != "SUCCESS"]

    logger.info("Final summary:")
    for row in summary_rows:
        logger.info(
            "table=%s raw_row_count=%s standardized_row_count=%s status=%s output_path=%s",
            row["table_name"],
            row["raw_row_count"],
            row["standardized_row_count"],
            row["status"],
            row["output_path"],
        )
    logger.info("summary_csv=%s", summary_path)

    if failed_rows:
        logger.error("final_run_result=FAILED failed_table_count=%s", len(failed_rows))
        return 1

    logger.info("final_run_result=SUCCESS")
    logger.info("Raw to standardized Spark processing completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
