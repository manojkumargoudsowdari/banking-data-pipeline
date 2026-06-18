import argparse
import csv
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path

import pyarrow.parquet as pq
from pyspark.sql import functions as F

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from spark.utils.model_config import CURATED_MODEL_CONFIGS
from spark.utils.spark_session import create_spark_session


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build curated banking dimensions and facts from standardized Parquet inputs."
    )
    parser.add_argument("--load-date", required=True, help="Load date in YYYY-MM-DD format.")
    parser.add_argument(
        "--input-dir",
        default="data/standardized",
        help="Base standardized input directory.",
    )
    parser.add_argument(
        "--output-dir",
        default="data/curated",
        help="Base curated output directory.",
    )
    parser.add_argument("--log-dir", default="logs/spark", help="Spark log and summary directory.")
    parser.add_argument(
        "--models",
        help="Optional comma-separated curated model list. Defaults to all configured models.",
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


def parse_models(models_arg):
    configured_models = list(CURATED_MODEL_CONFIGS)
    if not models_arg:
        return configured_models

    requested_models = [model.strip() for model in models_arg.split(",") if model.strip()]
    if not requested_models:
        raise ValueError("At least one model must be requested.")

    invalid_models = [model for model in requested_models if model not in CURATED_MODEL_CONFIGS]
    if invalid_models:
        invalid = ", ".join(invalid_models)
        allowed = ", ".join(configured_models)
        raise ValueError(f"Invalid model name(s): {invalid}. Allowed models: {allowed}")

    return requested_models


def configure_logging(log_dir):
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_path / f"curated_model_{run_timestamp}.log"

    logger = logging.getLogger("curated_model_builder")
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


def standardized_input_path(input_dir, table_name, load_date):
    return Path(input_dir) / table_name / f"load_date={load_date}" / f"{table_name}.parquet"


def read_standardized_table(spark, input_dir, table_name, load_date, temp_root):
    input_path = standardized_input_path(input_dir, table_name, load_date)
    if not input_path.exists():
        raise FileNotFoundError(f"Standardized input not found: {input_path}")

    compatible_dir = Path(temp_root) / table_name
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
    return spark.read.parquet(str(compatible_file)), input_path


def select_configured_columns(df, model_name):
    target_columns = CURATED_MODEL_CONFIGS[model_name]["target_columns"]
    missing_columns = [column for column in target_columns if column not in df.columns]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"Missing target column(s) for {model_name}: {missing}")
    return df.select(*target_columns)


def build_dimension(source_df, model_name):
    config = CURATED_MODEL_CONFIGS[model_name]
    return select_configured_columns(source_df, model_name).dropDuplicates(
        config["logical_primary_key"]
    )


def build_fact_transaction(transactions_df, accounts_df):
    transaction_count = transactions_df.count()
    account_lookup = accounts_df.select("account_id", "customer_id", "product_id").dropDuplicates(
        ["account_id"]
    )

    joined_df = transactions_df.alias("transactions").join(
        account_lookup.alias("accounts"),
        F.col("transactions.account_id") == F.col("accounts.account_id"),
        "left",
    )

    selected_df = joined_df.select(
        F.col("transactions.transaction_id").alias("transaction_id"),
        F.col("transactions.transaction_reference").alias("transaction_reference"),
        F.col("transactions.account_id").alias("account_id"),
        F.col("accounts.customer_id").alias("customer_id"),
        F.col("accounts.product_id").alias("product_id"),
        F.col("transactions.branch_id").alias("branch_id"),
        F.col("transactions.related_account_id").alias("related_account_id"),
        F.col("transactions.transaction_type").alias("transaction_type"),
        F.col("transactions.transaction_channel").alias("transaction_channel"),
        F.col("transactions.amount").alias("amount"),
        F.col("transactions.currency").alias("currency"),
        F.col("transactions.transaction_status").alias("transaction_status"),
        F.col("transactions.description").alias("description"),
        F.col("transactions.merchant_name").alias("merchant_name"),
        F.col("transactions.transaction_at").alias("transaction_at"),
        F.col("transactions.posted_at").alias("posted_at"),
        F.col("transactions.created_at").alias("created_at"),
        F.col("transactions.source_load_date").alias("source_load_date"),
        F.col("transactions.standardized_at_utc").alias("standardized_at_utc"),
    )
    output_df = select_configured_columns(selected_df, "fact_transaction").dropDuplicates(
        ["transaction_id"]
    )
    records_lost_to_join = max(transaction_count - joined_df.count(), 0)
    return output_df, records_lost_to_join


def build_fact_customer_risk_score(source_df):
    return select_configured_columns(source_df, "fact_customer_risk_score").dropDuplicates(
        ["risk_score_id"]
    )


def build_fact_daily_account_balance(accounts_df):
    # This is a derived account-day snapshot from the standardized account extract.
    # It is not an official banking ledger balance.
    balance_df = accounts_df.withColumn("balance_date", F.col("source_load_date").cast("date"))
    return select_configured_columns(balance_df, "fact_daily_account_balance").dropDuplicates(
        ["account_id", "balance_date"]
    )


def build_model(model_name, source_frames):
    if model_name == "dim_customer":
        return build_dimension(source_frames["customers"], model_name), 0
    if model_name == "dim_account":
        return build_dimension(source_frames["accounts"], model_name), 0
    if model_name == "dim_branch":
        return build_dimension(source_frames["branches"], model_name), 0
    if model_name == "dim_product":
        return build_dimension(source_frames["products"], model_name), 0
    if model_name == "fact_transaction":
        return build_fact_transaction(source_frames["transactions"], source_frames["accounts"])
    if model_name == "fact_customer_risk_score":
        return build_fact_customer_risk_score(source_frames["customer_risk_scores"]), 0
    if model_name == "fact_daily_account_balance":
        return build_fact_daily_account_balance(source_frames["accounts"]), 0
    raise ValueError(f"Unsupported model: {model_name}")


def count_duplicate_keys(df, logical_primary_key):
    return (
        df.groupBy(*logical_primary_key)
        .count()
        .where(F.col("count") > 1)
        .count()
    )


def count_null_foreign_keys(df, model_name):
    if CURATED_MODEL_CONFIGS[model_name]["model_type"] != "fact":
        return 0

    foreign_keys = [
        column
        for column in CURATED_MODEL_CONFIGS[model_name]["logical_foreign_keys"]
        if column in df.columns
    ]
    if not foreign_keys:
        return 0

    null_condition = F.lit(False)
    for column_name in foreign_keys:
        null_condition = null_condition | F.col(column_name).isNull()
    return df.where(null_condition).count()


def write_single_parquet(df, output_path):
    final_path = Path(output_path)
    final_path.parent.mkdir(parents=True, exist_ok=True)
    if final_path.exists():
        if final_path.is_dir():
            shutil.rmtree(final_path)
        else:
            final_path.unlink()

    pandas_df = df.toPandas()
    pandas_df.to_parquet(
        final_path,
        index=False,
        engine="pyarrow",
        coerce_timestamps="us",
        allow_truncated_timestamps=True,
    )


def write_summary_csv(summary_rows, log_dir, run_timestamp):
    summary_path = Path(log_dir) / f"curated_model_summary_{run_timestamp}.csv"
    fieldnames = [
        "model_name",
        "status",
        "source_tables",
        "output_row_count",
        "duplicate_key_count",
        "null_foreign_key_count",
        "input_paths",
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
        selected_models = parse_models(args.models)
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    logger, run_timestamp, log_file = configure_logging(args.log_dir)
    summary_rows = []
    spark = None
    temp_root = Path(args.output_dir) / f"_curated_read_tmp_{run_timestamp}"

    logger.info("Curated model build started.")
    logger.info("load_date=%s", load_date)
    logger.info("selected_models=%s", ",".join(selected_models))
    logger.info("input_dir=%s", args.input_dir)
    logger.info("output_dir=%s", args.output_dir)
    logger.info("log_file=%s", log_file)

    try:
        spark = create_spark_session("Banking Curated Warehouse Models")

        for model_name in selected_models:
            config = CURATED_MODEL_CONFIGS[model_name]
            source_tables = config["source_tables"]
            input_paths = [
                standardized_input_path(args.input_dir, table, load_date)
                for table in source_tables
            ]
            output_path = (
                Path(args.output_dir)
                / model_name
                / f"load_date={load_date}"
                / f"{model_name}.parquet"
            )

            logger.info("Starting model=%s", model_name)
            try:
                source_frames = {}
                for table_name in source_tables:
                    source_frames[table_name], _ = read_standardized_table(
                        spark,
                        args.input_dir,
                        table_name,
                        load_date,
                        temp_root / model_name,
                    )

                model_df, records_lost_to_join = build_model(model_name, source_frames)
                output_row_count = model_df.count()
                if output_row_count <= 0:
                    raise ValueError(f"Curated model {model_name} produced no rows.")

                duplicate_key_count = count_duplicate_keys(
                    model_df,
                    config["logical_primary_key"],
                )
                null_foreign_key_count = count_null_foreign_keys(model_df, model_name)

                write_single_parquet(model_df, output_path)
                parquet_row_count = pq.ParquetFile(output_path).metadata.num_rows
                if parquet_row_count != output_row_count:
                    raise ValueError(
                        "Curated Parquet row count mismatch: "
                        f"dataframe={output_row_count}, parquet={parquet_row_count}"
                    )

                logger.info("model=%s output_row_count=%s", model_name, output_row_count)
                logger.info("model=%s duplicate_key_count=%s", model_name, duplicate_key_count)
                logger.info(
                    "model=%s null_foreign_key_count=%s",
                    model_name,
                    null_foreign_key_count,
                )
                logger.info("model=%s records_lost_to_joins=%s", model_name, records_lost_to_join)
                logger.info("model=%s output_path=%s", model_name, output_path)
                logger.info("model=%s status=SUCCESS", model_name)

                summary_rows.append(
                    {
                        "model_name": model_name,
                        "status": "SUCCESS",
                        "source_tables": ",".join(source_tables),
                        "output_row_count": output_row_count,
                        "duplicate_key_count": duplicate_key_count,
                        "null_foreign_key_count": null_foreign_key_count,
                        "input_paths": ";".join(str(path) for path in input_paths),
                        "output_path": str(output_path),
                        "error_message": "",
                    }
                )
            except Exception as exc:
                logger.exception("model=%s status=FAILED error=%s", model_name, exc)
                summary_rows.append(
                    {
                        "model_name": model_name,
                        "status": "FAILED",
                        "source_tables": ",".join(source_tables),
                        "output_row_count": 0,
                        "duplicate_key_count": 0,
                        "null_foreign_key_count": 0,
                        "input_paths": ";".join(str(path) for path in input_paths),
                        "output_path": str(output_path),
                        "error_message": str(exc),
                    }
                )
    finally:
        if spark is not None:
            spark.stop()
        if temp_root.exists():
            shutil.rmtree(temp_root)

    summary_path = write_summary_csv(summary_rows, args.log_dir, run_timestamp)
    failed_models = [row for row in summary_rows if row["status"] != "SUCCESS"]

    logger.info("Final summary:")
    for row in summary_rows:
        logger.info(
            "model=%s status=%s output_row_count=%s duplicate_key_count=%s "
            "null_foreign_key_count=%s output_path=%s",
            row["model_name"],
            row["status"],
            row["output_row_count"],
            row["duplicate_key_count"],
            row["null_foreign_key_count"],
            row["output_path"],
        )
    logger.info("summary_csv=%s", summary_path)

    if failed_models:
        logger.error("final_run_result=FAILED failed_model_count=%s", len(failed_models))
        return 1

    logger.info("final_run_result=SUCCESS")
    logger.info("Curated model build completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
