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

from spark.dq.dq_config import (
    ACCEPTED_VALUE_RULES,
    PYSPARK_DQ_CONFIGS,
    RANGE_RULES,
    REFERENTIAL_INTEGRITY_RULES,
    SOURCE_TO_TARGET_DATASETS,
)
from spark.utils.spark_session import create_spark_session

BUSINESS_RULE_COLUMNS = [
    "load_date",
    "dataset_name",
    "check_category",
    "check_name",
    "failed_record_count",
    "status",
    "details",
]

EXCEPTION_COLUMNS = [
    "check_category",
    "check_name",
    "dataset_name",
    "business_key",
    "failed_column",
    "failed_value",
    "error_message",
    "load_date",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Profile curated datasets and run PySpark data quality rules."
    )
    parser.add_argument("--load-date", required=True, help="Load date in YYYY-MM-DD format.")
    parser.add_argument("--input-dir", default="data/curated")
    parser.add_argument("--standardized-dir", default="data/standardized")
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


def parquet_input_path(base_dir, entity_name, load_date):
    return (
        Path(base_dir)
        / entity_name
        / f"load_date={load_date}"
        / f"{entity_name}.parquet"
    )


def read_parquet_dataset(spark, input_path, temp_dir):
    if not input_path.is_file():
        raise FileNotFoundError(f"Parquet input not found: {input_path}")

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
    return spark.read.parquet(str(compatible_file)).cache()


def profile_dataset(df, dataset_name, config, load_date):
    row_count = df.count()
    actual_columns = df.columns
    expected_columns = config["expected_columns"]
    required_columns = config["required_columns"]
    return {
        "load_date": load_date,
        "dataset_name": dataset_name,
        "row_count": row_count,
        "column_count": len(actual_columns),
        "expected_column_count": len(expected_columns),
        "missing_expected_columns": ",".join(
            column for column in expected_columns if column not in actual_columns
        ),
        "extra_columns": ",".join(
            column for column in actual_columns if column not in expected_columns
        ),
        "missing_required_columns": ",".join(
            column for column in required_columns if column not in actual_columns
        ),
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


def create_foundation_rule_results(df, dataset_profile, config):
    dataset_name = dataset_profile["dataset_name"]
    load_date = dataset_profile["load_date"]
    missing_expected = dataset_profile["missing_expected_columns"]
    extra_columns = dataset_profile["extra_columns"]
    missing_required = dataset_profile["missing_required_columns"]
    schema_failure_count = len([value for value in missing_expected.split(",") if value])
    schema_failure_count += len([value for value in extra_columns.split(",") if value])
    required_failure_count = len([value for value in missing_required.split(",") if value])

    key_columns = config["logical_key_columns"]
    missing_keys = [column for column in key_columns if column not in df.columns]
    if missing_keys:
        duplicate_count = len(missing_keys)
        duplicate_details = f"missing_logical_key_columns={','.join(missing_keys)}"
    else:
        duplicate_count = (
            df.groupBy(*key_columns).count().where(F.col("count") > 1).count()
        )
        duplicate_details = f"logical_key_columns={','.join(key_columns)}"

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
        {
            "load_date": load_date,
            "dataset_name": dataset_name,
            "rule_name": "duplicate_logical_key_check",
            "status": "PASS" if duplicate_count == 0 else "FAIL",
            "failed_record_count": duplicate_count,
            "details": duplicate_details,
        },
    ]


def business_key_expression(dataset_name, config):
    available_keys = config["logical_key_columns"]
    return F.concat_ws(
        "|",
        *[
            F.coalesce(F.col(column).cast("string"), F.lit("<NULL>"))
            for column in available_keys
        ],
    )


def collect_exceptions(
    invalid_df,
    dataset_name,
    config,
    category,
    check_name,
    failed_column,
    error_message,
    load_date,
):
    if failed_column in invalid_df.columns:
        failed_value = F.coalesce(F.col(failed_column).cast("string"), F.lit("<NULL>"))
    else:
        failed_value = F.lit("<UNAVAILABLE>")

    rows = (
        invalid_df.select(
            F.lit(category).alias("check_category"),
            F.lit(check_name).alias("check_name"),
            F.lit(dataset_name).alias("dataset_name"),
            business_key_expression(dataset_name, config).alias("business_key"),
            F.lit(failed_column).alias("failed_column"),
            failed_value.alias("failed_value"),
            F.lit(error_message).alias("error_message"),
            F.lit(load_date).alias("load_date"),
        )
        .limit(100)
        .collect()
    )
    return [row.asDict() for row in rows]


def rule_result(load_date, dataset_name, category, check_name, failed_count, details):
    return {
        "load_date": load_date,
        "dataset_name": dataset_name,
        "check_category": category,
        "check_name": check_name,
        "failed_record_count": int(failed_count),
        "status": "PASS" if int(failed_count) == 0 else "FAIL",
        "details": details,
    }


def run_accepted_value_rules(df, dataset_name, config, load_date):
    results = []
    exceptions = []
    for column_name, accepted_values in ACCEPTED_VALUE_RULES.get(dataset_name, {}).items():
        if column_name not in df.columns:
            continue
        invalid_df = df.where(
            F.col(column_name).isNull() | ~F.col(column_name).isin(accepted_values)
        )
        failed_count = invalid_df.count()
        check_name = f"{column_name}_accepted_values"
        results.append(
            rule_result(
                load_date,
                dataset_name,
                "ACCEPTED_VALUE",
                check_name,
                failed_count,
                f"accepted_values={','.join(accepted_values)}",
            )
        )
        if failed_count:
            exceptions.extend(
                collect_exceptions(
                    invalid_df,
                    dataset_name,
                    config,
                    "ACCEPTED_VALUE",
                    check_name,
                    column_name,
                    f"{column_name} is outside the configured accepted values.",
                    load_date,
                )
            )
    return results, exceptions


def range_condition(column_name, rule):
    condition = F.lit(False)
    column = F.col(column_name)
    if rule.get("required"):
        condition = condition | column.isNull()
    if "minimum" in rule:
        condition = condition | (column.isNotNull() & (column < F.lit(rule["minimum"])))
    if "minimum_exclusive" in rule:
        condition = condition | (
            column.isNull() | (column <= F.lit(rule["minimum_exclusive"]))
        )
    if "maximum" in rule:
        condition = condition | (column.isNotNull() & (column > F.lit(rule["maximum"])))
    return condition


def run_range_rules(df, dataset_name, config, load_date):
    results = []
    exceptions = []
    for column_name, range_rule in RANGE_RULES.get(dataset_name, {}).items():
        if column_name not in df.columns:
            continue
        invalid_df = df.where(range_condition(column_name, range_rule))
        failed_count = invalid_df.count()
        check_name = f"{column_name}_range_check"
        results.append(
            rule_result(
                load_date,
                dataset_name,
                "RANGE",
                check_name,
                failed_count,
                f"range_config={range_rule}",
            )
        )
        if failed_count:
            exceptions.extend(
                collect_exceptions(
                    invalid_df,
                    dataset_name,
                    config,
                    "RANGE",
                    check_name,
                    column_name,
                    f"{column_name} is outside the configured range.",
                    load_date,
                )
            )
    return results, exceptions


def run_referential_rules(
    df,
    dataset_name,
    config,
    load_date,
    get_curated_frame,
):
    results = []
    exceptions = []
    for reference_rule in REFERENTIAL_INTEGRITY_RULES.get(dataset_name, []):
        column_name = reference_rule["column"]
        reference_dataset = reference_rule["reference_dataset"]
        reference_column = reference_rule["reference_column"]
        if column_name not in df.columns:
            continue

        source_df = df
        if reference_rule["allow_null"]:
            source_df = source_df.where(F.col(column_name).isNotNull())
        reference_df = get_curated_frame(reference_dataset).select(
            F.col(reference_column).alias("_reference_key")
        ).dropDuplicates()
        invalid_df = source_df.join(
            reference_df,
            source_df[column_name] == reference_df["_reference_key"],
            "left_anti",
        )
        failed_count = invalid_df.count()
        check_name = f"{column_name}_references_{reference_dataset}"
        results.append(
            rule_result(
                load_date,
                dataset_name,
                "REFERENTIAL_INTEGRITY",
                check_name,
                failed_count,
                f"{column_name} -> {reference_dataset}.{reference_column}",
            )
        )
        if failed_count:
            exceptions.extend(
                collect_exceptions(
                    invalid_df,
                    dataset_name,
                    config,
                    "REFERENTIAL_INTEGRITY",
                    check_name,
                    column_name,
                    f"{column_name} does not resolve to {reference_dataset}.{reference_column}.",
                    load_date,
                )
            )
    return results, exceptions


def run_reconciliation_rule(
    curated_df,
    standardized_df,
    dataset_name,
    config,
    source_table,
    load_date,
):
    curated_count = curated_df.count()
    source_count = standardized_df.count()
    failed_count = abs(source_count - curated_count)
    check_name = f"{source_table}_to_{dataset_name}_row_count"
    result = rule_result(
        load_date,
        dataset_name,
        "RECONCILIATION",
        check_name,
        failed_count,
        f"standardized_row_count={source_count}; curated_row_count={curated_count}",
    )
    exceptions = []
    if failed_count:
        exceptions.append(
            {
                "check_category": "RECONCILIATION",
                "check_name": check_name,
                "dataset_name": dataset_name,
                "business_key": "<ROW_COUNT>",
                "failed_column": "row_count",
                "failed_value": f"source={source_count};target={curated_count}",
                "error_message": "Standardized and curated row counts do not match.",
                "load_date": load_date,
            }
        )
    return [result], exceptions


def grouped_count_mismatch(source_df, target_df, column_name):
    source_counts = source_df.groupBy(column_name).count().withColumnRenamed("count", "source_count")
    target_counts = target_df.groupBy(column_name).count().withColumnRenamed("count", "target_count")
    return (
        source_counts.join(target_counts, column_name, "full")
        .fillna(0, subset=["source_count", "target_count"])
        .where(F.col("source_count") != F.col("target_count"))
    )


def run_control_total_rules(
    curated_df,
    standardized_df,
    dataset_name,
    config,
    load_date,
):
    results = []
    exceptions = []

    if dataset_name == "fact_transaction":
        source_total = standardized_df.agg(F.sum("amount")).first()[0] or 0
        target_total = curated_df.agg(F.sum("amount")).first()[0] or 0
        failed_count = 0 if source_total == target_total else 1
        check_name = "transaction_amount_control_total"
        results.append(
            rule_result(
                load_date,
                dataset_name,
                "CONTROL_TOTAL",
                check_name,
                failed_count,
                f"standardized_total={source_total}; curated_total={target_total}",
            )
        )
        if failed_count:
            exceptions.append(
                {
                    "check_category": "CONTROL_TOTAL",
                    "check_name": check_name,
                    "dataset_name": dataset_name,
                    "business_key": "<AGGREGATE>",
                    "failed_column": "amount",
                    "failed_value": f"source={source_total};target={target_total}",
                    "error_message": "Transaction amount control totals do not match.",
                    "load_date": load_date,
                }
            )

        mismatch_df = grouped_count_mismatch(
            standardized_df,
            curated_df,
            "transaction_type",
        )
        mismatch_count = mismatch_df.count()
        check_name = "transaction_type_count_control"
        results.append(
            rule_result(
                load_date,
                dataset_name,
                "CONTROL_TOTAL",
                check_name,
                mismatch_count,
                "Counts by transaction_type must match.",
            )
        )
        if mismatch_count:
            for row in mismatch_df.limit(100).collect():
                exceptions.append(
                    {
                        "check_category": "CONTROL_TOTAL",
                        "check_name": check_name,
                        "dataset_name": dataset_name,
                        "business_key": str(row["transaction_type"]),
                        "failed_column": "transaction_type",
                        "failed_value": (
                            f"source={row['source_count']};target={row['target_count']}"
                        ),
                        "error_message": "Transaction type counts do not match.",
                        "load_date": load_date,
                    }
                )

    if dataset_name == "dim_account":
        mismatch_df = grouped_count_mismatch(
            standardized_df,
            curated_df,
            "account_status",
        )
        mismatch_count = mismatch_df.count()
        check_name = "account_status_count_control"
        results.append(
            rule_result(
                load_date,
                dataset_name,
                "CONTROL_TOTAL",
                check_name,
                mismatch_count,
                "Counts by account_status must match.",
            )
        )
        if mismatch_count:
            for row in mismatch_df.limit(100).collect():
                exceptions.append(
                    {
                        "check_category": "CONTROL_TOTAL",
                        "check_name": check_name,
                        "dataset_name": dataset_name,
                        "business_key": str(row["account_status"]),
                        "failed_column": "account_status",
                        "failed_value": (
                            f"source={row['source_count']};target={row['target_count']}"
                        ),
                        "error_message": "Account status counts do not match.",
                        "load_date": load_date,
                    }
                )
    return results, exceptions


def write_result_set(rows, output_dir, stem, columns=None):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    dataframe = pd.DataFrame(rows, columns=columns)
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
        "accepted_value_failed_count",
        "range_failed_count",
        "referential_integrity_failed_count",
        "reconciliation_failed_count",
        "control_total_failed_count",
        "exception_record_count",
        "input_path",
        "error_message",
    ]
    with summary_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)
    return summary_path


def category_failed_count(results, category):
    return sum(
        int(result["failed_record_count"])
        for result in results
        if result["check_category"] == category
    )


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
    foundation_rule_results = []
    business_rule_results = []
    exception_records = []
    summary_rows = []
    curated_frames = {}
    standardized_frames = {}
    spark = None

    logger.info("PySpark DQ validation started.")
    logger.info("load_date=%s", load_date)
    logger.info("datasets=%s", ",".join(selected_datasets))
    logger.info("output_dir=%s", output_dir)
    logger.info("log_file=%s", log_file)

    try:
        spark = create_spark_session("Banking PySpark DQ Validation")

        def get_curated_frame(dataset_name):
            if dataset_name not in curated_frames:
                path = parquet_input_path(args.input_dir, dataset_name, load_date)
                curated_frames[dataset_name] = read_parquet_dataset(
                    spark,
                    path,
                    temp_root / "curated" / dataset_name,
                )
            return curated_frames[dataset_name]

        def get_standardized_frame(table_name):
            if table_name not in standardized_frames:
                path = parquet_input_path(args.standardized_dir, table_name, load_date)
                standardized_frames[table_name] = read_parquet_dataset(
                    spark,
                    path,
                    temp_root / "standardized" / table_name,
                )
            return standardized_frames[table_name]

        for dataset_name in selected_datasets:
            config = PYSPARK_DQ_CONFIGS[dataset_name]
            input_path = parquet_input_path(args.input_dir, dataset_name, load_date)
            logger.info("Starting dataset=%s input_path=%s", dataset_name, input_path)
            try:
                df = get_curated_frame(dataset_name)
                dataset_profile = profile_dataset(df, dataset_name, config, load_date)
                dataset_column_profiles = profile_columns(
                    df,
                    dataset_name,
                    config,
                    load_date,
                    dataset_profile["row_count"],
                )
                dataset_foundation_rules = create_foundation_rule_results(
                    df,
                    dataset_profile,
                    config,
                )

                dataset_business_results = []
                dataset_exceptions = []

                results, exceptions = run_accepted_value_rules(
                    df, dataset_name, config, load_date
                )
                dataset_business_results.extend(results)
                dataset_exceptions.extend(exceptions)

                results, exceptions = run_range_rules(
                    df, dataset_name, config, load_date
                )
                dataset_business_results.extend(results)
                dataset_exceptions.extend(exceptions)

                results, exceptions = run_referential_rules(
                    df,
                    dataset_name,
                    config,
                    load_date,
                    get_curated_frame,
                )
                dataset_business_results.extend(results)
                dataset_exceptions.extend(exceptions)

                source_table = SOURCE_TO_TARGET_DATASETS.get(dataset_name)
                if source_table:
                    standardized_df = get_standardized_frame(source_table)
                    results, exceptions = run_reconciliation_rule(
                        df,
                        standardized_df,
                        dataset_name,
                        config,
                        source_table,
                        load_date,
                    )
                    dataset_business_results.extend(results)
                    dataset_exceptions.extend(exceptions)

                    results, exceptions = run_control_total_rules(
                        df,
                        standardized_df,
                        dataset_name,
                        config,
                        load_date,
                    )
                    dataset_business_results.extend(results)
                    dataset_exceptions.extend(exceptions)

                failed_foundation_count = sum(
                    1 for result in dataset_foundation_rules if result["status"] == "FAIL"
                )
                failed_business_count = sum(
                    1 for result in dataset_business_results if result["status"] == "FAIL"
                )

                dataset_profiles.append(dataset_profile)
                column_profiles.extend(dataset_column_profiles)
                foundation_rule_results.extend(dataset_foundation_rules)
                business_rule_results.extend(dataset_business_results)
                exception_records.extend(dataset_exceptions)
                summary_rows.append(
                    {
                        "dataset_name": dataset_name,
                        "status": "SUCCESS",
                        "row_count": dataset_profile["row_count"],
                        "column_profile_count": len(dataset_column_profiles),
                        "rule_count": (
                            len(dataset_foundation_rules) + len(dataset_business_results)
                        ),
                        "failed_rule_count": (
                            failed_foundation_count + failed_business_count
                        ),
                        "accepted_value_failed_count": category_failed_count(
                            dataset_business_results, "ACCEPTED_VALUE"
                        ),
                        "range_failed_count": category_failed_count(
                            dataset_business_results, "RANGE"
                        ),
                        "referential_integrity_failed_count": category_failed_count(
                            dataset_business_results, "REFERENTIAL_INTEGRITY"
                        ),
                        "reconciliation_failed_count": category_failed_count(
                            dataset_business_results, "RECONCILIATION"
                        ),
                        "control_total_failed_count": category_failed_count(
                            dataset_business_results, "CONTROL_TOTAL"
                        ),
                        "exception_record_count": len(dataset_exceptions),
                        "input_path": str(input_path),
                        "error_message": "",
                    }
                )
                logger.info(
                    "dataset=%s row_count=%s failed_rule_count=%s exception_record_count=%s status=SUCCESS",
                    dataset_name,
                    dataset_profile["row_count"],
                    failed_foundation_count + failed_business_count,
                    len(dataset_exceptions),
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
                        "accepted_value_failed_count": 0,
                        "range_failed_count": 0,
                        "referential_integrity_failed_count": 0,
                        "reconciliation_failed_count": 0,
                        "control_total_failed_count": 0,
                        "exception_record_count": 0,
                        "input_path": str(input_path),
                        "error_message": str(exc),
                    }
                )
    finally:
        for frame in curated_frames.values():
            frame.unpersist()
        for frame in standardized_frames.values():
            frame.unpersist()
        if spark is not None:
            spark.stop()
        if temp_root.exists():
            shutil.rmtree(temp_root)

    execution_failures = [row for row in summary_rows if row["status"] == "FAILED"]
    if dataset_profiles:
        write_result_set(dataset_profiles, output_dir, "dataset_profile_results")
        write_result_set(column_profiles, output_dir, "column_profile_results")
        write_result_set(foundation_rule_results, output_dir, "rule_results")
        write_result_set(
            business_rule_results,
            output_dir,
            "business_rule_results",
            BUSINESS_RULE_COLUMNS,
        )
        write_result_set(
            exception_records,
            output_dir,
            "exception_records",
            EXCEPTION_COLUMNS,
        )

    summary_path = write_summary(summary_rows, args.log_dir, run_timestamp)
    logger.info("Final summary:")
    for row in summary_rows:
        logger.info(
            "dataset=%s status=%s row_count=%s rule_count=%s failed_rule_count=%s "
            "exception_record_count=%s",
            row["dataset_name"],
            row["status"],
            row["row_count"],
            row["rule_count"],
            row["failed_rule_count"],
            row["exception_record_count"],
        )
    logger.info("summary_csv=%s", summary_path)

    if execution_failures:
        logger.error(
            "final_run_result=FAILED execution_failure_count=%s",
            len(execution_failures),
        )
        return 1

    logger.info("final_run_result=SUCCESS")
    logger.info("PySpark DQ validation completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
