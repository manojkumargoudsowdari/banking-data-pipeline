# PySpark Data Quality Profiling

## Phase 7A Purpose

Phase 7A adds a foundational PySpark data quality profiling layer over curated banking datasets. It focuses on dataset structure, required columns, nulls, distinct values, and duplicate logical keys.

This phase does not implement a complete business-rule engine, SQL validation, OpenMetadata integration, governance artifacts, lineage, stewardship automation, or Agile/JIRA evidence.

## Inputs

The runner reads curated Parquet files from:

```text
data/curated/<dataset>/load_date=<YYYY-MM-DD>/<dataset>.parquet
```

Supported datasets:

- `dim_customer`
- `dim_account`
- `dim_branch`
- `dim_product`
- `fact_transaction`
- `fact_customer_risk_score`
- `fact_daily_account_balance`

## Configuration

`spark/dq/dq_config.py` defines, per dataset:

- Expected columns
- Required columns
- Logical key columns
- Columns selected for profiling

Logical keys are data-quality expectations. Parquet does not enforce key constraints.

## Profiles And Rules

Dataset profiles report:

- Row count
- Actual and expected column counts
- Missing expected columns
- Extra columns
- Missing required columns

Column profiles report:

- Null count
- Non-null count
- Distinct count

Foundational rule results include:

- `schema_expected_columns_check`
- `required_columns_check`
- `duplicate_logical_key_check`

Rule failures are written as results and do not crash the job. Configuration, input-read, or execution failures cause a nonzero process exit.

## Outputs

Results are written under:

```text
data/dq_results/pyspark/load_date=<YYYY-MM-DD>/
```

Files:

- `dataset_profile_results.csv`
- `dataset_profile_results.parquet`
- `column_profile_results.csv`
- `column_profile_results.parquet`
- `rule_results.csv`
- `rule_results.parquet`

Runtime summaries are written to:

```text
logs/dq/pyspark_dq_summary_YYYYMMDD_HHMMSS.csv
```

These outputs provide practical evidence for discussing profiling, schema drift, completeness, uniqueness, and logical keys in data quality interviews.

## Phase 7B Business Rules

Phase 7B extends the same PySpark runner with:

- Accepted-value checks for customer, account, transaction, and risk classifications.
- Numeric range checks for transaction amounts, account balances, and risk scores.
- Referential-integrity checks implemented with Spark joins.
- Standardized-to-curated row-count reconciliation.
- Spark aggregation control totals for transaction amounts and grouped counts.
- Bounded exception records, limited to 100 records per exception type.

The implementation uses actual curated column names. For example, transaction value is stored in `amount`, account type is not present in `dim_account`, and risk scores use the source scale of 0 through 1000.

Additional outputs:

- `business_rule_results.csv`
- `business_rule_results.parquet`
- `exception_records.csv`
- `exception_records.parquet`

Business-rule failures are evidence and do not terminate the runner. Missing input files, invalid configuration, and Spark execution errors return a nonzero exit code.

## PySpark Versus Phase 6 SQL

Phase 6 uses DuckDB SQL to query Parquet directly and demonstrates SQL validation, reconciliation, and exception reporting.

Phase 7 uses Spark DataFrames:

- Referential checks use distributed joins.
- Control totals use Spark aggregations and grouped comparisons.
- Exceptions are selected from failed DataFrame conditions.
- The framework can scale beyond the local practice data without rewriting checks as database SQL.

The SQL and PySpark layers intentionally overlap in validation categories so the project demonstrates two common implementation approaches.
