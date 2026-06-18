import argparse
import csv
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
from pyspark.sql import functions as F

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from spark.dq.dq_config import PYSPARK_DQ_CONFIGS
from spark.utils.spark_session import create_spark_session


def parse_args():
    parser = argparse.ArgumentParser(
        description="Profile curated banking datasets and run foundational PySpark DQ checks."
    )
    parser.add_argument("--load-date", required=True, help="Load date in YYYY-MM-DD format.")
    parser.add_argument("--input-dir", default="data/curated")
    parser.add_argument("--output-dir", default="data/dq_results/pyspark")
    parser.add_argument("--log-dir", default="logs/dq")
    parser.add_argument(
        "--datasets",
        help="Optional comma-separated curated dataset list. Defaults to all configured datasets.",
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


def parse_datasets(datasets_arg):
    configured = list(PYSPARK_DQ_CONFIGS)
    if not datasets_arg:
        return configured

    requested = [dataset.strip() for dataset in datasets_arg.split(",") if dataset.strip()]
    if not requested:
        raise ValueError("At least one dataset must be requested.")

    invalid = [dataset for dataset in requested if dataset not in PYSPARK_DQ_CONFIGS]
    if invalid:
        raise ValueError(
            f"Invalid dataset name(s): {', '.join(invalid)}. "
            f"Allowed datasets: {', '.join(configured)}"
        )
    return requested


def configure_logging(log_dir):
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_path / f"pyspark_dq_{run_timestamp}.log"

    logger = logging.getLogger("pyspark_dq")
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


def curated_input_path(input_dir, dataset_name, load_date):
    return (
        Path(input_dir)
        / dataset_name
        / f"load_date={load_date}"
        / f"{dataset_name}.parquet"
    )


def read_curated_dataset(spark, input_path, temp_dir):
    if not input_path.is_file():
        raise FileNotFoundError(f"Curated input not found: {input_path}")

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
    return spark.read.parquet(str(compatible_file))


def profile_dataset(df, dataset_name, config, load_date):
    row_count = df.count()
    actual_columns = df.columns
    expected_columns = config["expected_columns"]
    required_columns = config["required_columns"]

    missing_expected = [column for column in expected_columns if column not in actual_columns]
    extra_columns = [column for column in actual_columns if column not in expected_columns]
    missing_required = [column for column in required_columns if column not in actual_columns]

    return {
        "load_date": load_date,
        "dataset_name": dataset_name,
        "row_count": row_count,
        "column_count": len(actual_columns),
        "expected_column_count": len(expected_columns),
        "missing_expected_columns": ",".join(missing_expected),
        "extra_columns": ",".join(extra_columns),
        "missing_required_columns": ",".join(missing_required),
    }


def profile_columns(df, dataset_name, config, load_date, row_count):
    results = []
    for column_name in config["profile_columns"]:
        if column_name not in df.columns:
            continue
        metrics = df.agg(
            F.sum(F.when(F.col(column_name).isNull(), 1).otherwise(0)).alias("null_count"),
            F.countDistinct(F.col(column_name)).alias("distinct_count"),
        ).first()
        null_count = int(metrics["null_count"] or 0)
        results.append(
            {
                "load_date": load_date,
                "dataset_name": dataset_name,
                "column_name": column_name,
                "null_count": null_count,
                "non_null_count": row_count - null_count,
                "distinct_count": int(metrics["distinct_count"] or 0),
            }
        )
    return results


def count_duplicate_key_combinations(df, logical_key_columns):
    if any(column not in df.columns for column in logical_key_columns):
        return 0
    return (
        df.groupBy(*logical_key_columns)
        .count()
        .where(F.col("count") > 1)
        .count()
    )


def create_rule_results(dataset_profile, config):
    dataset_name = dataset_profile["dataset_name"]
    load_date = dataset_profile["load_date"]
    missing_expected = dataset_profile["missing_expected_columns"]
    extra_columns = dataset_profile["extra_columns"]
    missing_required = dataset_profile["missing_required_columns"]

    schema_failure_count = len([value for value in missing_expected.split(",") if value])
    schema_failure_count += len([value for value in extra_columns.split(",") if value])
    required_failure_count = len([value for value in missing_required.split(",") if value])

    return [
        {
            "load_date": load_date,
            "dataset_name": dataset_name,
            "rule_name": "schema_expected_columns_check",
            "status": "PASS" if schema_failure_count == 0 else "FAIL",
            "failed_record_count": schema_failure_count,
            "details": (
                f"missing_expected_columns={missing_expected or '<none>'}; "
                f"extra_columns={extra_columns or '<none>'}"
            ),
        },
        {
            "load_date": load_date,
            "dataset_name": dataset_name,
            "rule_name": "required_columns_check",
            "status": "PASS" if required_failure_count == 0 else "FAIL",
            "failed_record_count": required_failure_count,
            "details": f"missing_required_columns={missing_required or '<none>'}",
        },
    ]


def duplicate_rule_result(df, dataset_name, config, load_date):
    key_columns = config["logical_key_columns"]
    missing_keys = [column for column in key_columns if column not in df.columns]
    if missing_keys:
        return {
            "load_date": load_date,
            "dataset_name": dataset_name,
            "rule_name": "duplicate_logical_key_check",
            "status": "FAIL",
            "failed_record_count": len(missing_keys),
            "details": f"missing_logical_key_columns={','.join(missing_keys)}",
        }

    duplicate_count = count_duplicate_key_combinations(df, key_columns)
    return {
        "load_date": load_date,
        "dataset_name": dataset_name,
        "rule_name": "duplicate_logical_key_check",
        "status": "PASS" if duplicate_count == 0 else "FAIL",
        "failed_record_count": duplicate_count,
        "details": f"logical_key_columns={','.join(key_columns)}",
    }


def write_result_set(rows, output_dir, stem):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    dataframe = pd.DataFrame(rows)
    csv_path = output_path / f"{stem}.csv"
    parquet_path = output_path / f"{stem}.parquet"
    dataframe.to_csv(csv_path, index=False)
    dataframe.to_parquet(
        parquet_path,
        index=False,
        engine="pyarrow",
        coerce_timestamps="us",
        allow_truncated_timestamps=True,
    )
    return csv_path, parquet_path


def write_summary(summary_rows, log_dir, run_timestamp):
    summary_path = Path(log_dir) / f"pyspark_dq_summary_{run_timestamp}.csv"
    fieldnames = [
        "dataset_name",
        "status",
        "row_count",
        "column_profile_count",
        "rule_count",
        "failed_rule_count",
        "input_path",
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
        selected_datasets = parse_datasets(args.datasets)
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    logger, run_timestamp, log_file = configure_logging(args.log_dir)
    output_dir = Path(args.output_dir) / f"load_date={load_date}"
    temp_root = output_dir / f"_dq_read_tmp_{run_timestamp}"
    dataset_profiles = []
    column_profiles = []
    rule_results = []
    summary_rows = []
    spark = None

    logger.info("PySpark DQ profiling started.")
    logger.info("load_date=%s", load_date)
    logger.info("datasets=%s", ",".join(selected_datasets))
    logger.info("output_dir=%s", output_dir)
    logger.info("log_file=%s", log_file)

    try:
        spark = create_spark_session("Banking PySpark DQ Profiling")

        for dataset_name in selected_datasets:
            config = PYSPARK_DQ_CONFIGS[dataset_name]
            input_path = curated_input_path(args.input_dir, dataset_name, load_date)
            logger.info("Starting dataset=%s input_path=%s", dataset_name, input_path)
            try:
                df = read_curated_dataset(
                    spark,
                    input_path,
                    temp_root / dataset_name,
                ).cache()

                dataset_profile = profile_dataset(
                    df,
                    dataset_name,
                    config,
                    load_date,
                )
                dataset_column_profiles = profile_columns(
                    df,
                    dataset_name,
                    config,
                    load_date,
                    dataset_profile["row_count"],
                )
                dataset_rule_results = create_rule_results(dataset_profile, config)
                dataset_rule_results.append(
                    duplicate_rule_result(df, dataset_name, config, load_date)
                )
                df.unpersist()

                failed_rule_count = sum(
                    1 for result in dataset_rule_results if result["status"] == "FAIL"
                )
                dataset_profiles.append(dataset_profile)
                column_profiles.extend(dataset_column_profiles)
                rule_results.extend(dataset_rule_results)
                summary_rows.append(
                    {
                        "dataset_name": dataset_name,
                        "status": "SUCCESS",
                        "row_count": dataset_profile["row_count"],
                        "column_profile_count": len(dataset_column_profiles),
                        "rule_count": len(dataset_rule_results),
                        "failed_rule_count": failed_rule_count,
                        "input_path": str(input_path),
                        "error_message": "",
                    }
                )
                logger.info(
                    "dataset=%s row_count=%s column_count=%s failed_rule_count=%s status=SUCCESS",
                    dataset_name,
                    dataset_profile["row_count"],
                    dataset_profile["column_count"],
                    failed_rule_count,
                )
            except Exception as exc:
                logger.exception("dataset=%s status=FAILED error=%s", dataset_name, exc)
                summary_rows.append(
                    {
                        "dataset_name": dataset_name,
                        "status": "FAILED",
                        "row_count": 0,
                        "column_profile_count": 0,
                        "rule_count": 0,
                        "failed_rule_count": 0,
                        "input_path": str(input_path),
                        "error_message": str(exc),
                    }
                )
    finally:
        if spark is not None:
            spark.stop()
        if temp_root.exists():
            shutil.rmtree(temp_root)

    execution_failures = [row for row in summary_rows if row["status"] == "FAILED"]
    if dataset_profiles:
        write_result_set(dataset_profiles, output_dir, "dataset_profile_results")
        write_result_set(column_profiles, output_dir, "column_profile_results")
        write_result_set(rule_results, output_dir, "rule_results")

    summary_path = write_summary(summary_rows, args.log_dir, run_timestamp)
    logger.info("Final summary:")
    for row in summary_rows:
        logger.info(
            "dataset=%s status=%s row_count=%s rule_count=%s failed_rule_count=%s",
            row["dataset_name"],
            row["status"],
            row["row_count"],
            row["rule_count"],
            row["failed_rule_count"],
        )
    logger.info("summary_csv=%s", summary_path)

    if execution_failures:
        logger.error(
            "final_run_result=FAILED execution_failure_count=%s",
            len(execution_failures),
        )
        return 1

    logger.info("final_run_result=SUCCESS")
    logger.info("PySpark DQ profiling completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
