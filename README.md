# Banking Data Governance & Data Quality Pipeline

This repository is a hands-on practice lab for data governance, data catalog, data lineage, data quality, SQL, PySpark, Python scripting, OpenMetadata, Agile/Scrum/SDLC, data modeling, and data warehousing.

The project is being rebuilt as a governance-first banking data platform lab. Phase 1 prepares the repository foundation only: folder structure, active documentation, safe environment examples, and cleanup of copied runtime artifacts.

## Current Phase

Phase 1 is limited to repository cleanup and foundation setup.

Included in Phase 1:

- Keep the Faker-based banking data generator.
- Keep the PostgreSQL source schema.
- Prepare folders for later ingestion, Spark, SQL validation, governance, OpenMetadata, Agile, and data zones.
- Rewrite active documentation around the governance and data quality project direction.
- Archive copied legacy components that are out of scope for this version.

Not included in Phase 1:

- No PySpark jobs.
- No OpenMetadata installation or configuration.
- No governance artifacts.
- No data quality logic.
- No SQL validation implementation.

## Project Direction

This is not a dbt-first project.

dbt, Kafka, Debezium, Airflow, Snowflake, Power BI, and streaming-first implementation patterns are legacy/out-of-scope for this version. Existing copied code for those tools has been moved under `legacy/` for reference only.

Future phases will add:

- Python extraction and ingestion scripts.
- Raw data landing using local Parquet or MinIO.
- PySpark processing jobs.
- Curated warehouse-style tables.
- SQL and PySpark data quality checks.
- OpenMetadata catalog, lineage, and governance integration.
- Stewardship workflows, issue tracking, and Agile evidence.

## Active Repository Structure

- `data-generator/` - Faker-based synthetic banking source data generation.
- `postgres/` - PostgreSQL source schema for customers, accounts, and transactions.
- `python/ingestion/` - placeholder for future extraction and ingestion scripts.
- `python/automation/` - placeholder for future automation scripts.
- `spark/jobs/` - placeholder for future PySpark processing jobs.
- `spark/dq/` - placeholder for future PySpark data quality checks.
- `sql/validation/` - placeholder for future SQL validation checks.
- `governance/` - placeholder for future governance artifacts.
- `openmetadata/` - placeholder for future OpenMetadata setup notes and configs.
- `agile/` - placeholder for future Agile/Scrum/SDLC evidence.
- `data/raw/` - local raw landing zone, ignored by Git.
- `data/curated/` - local curated output zone, ignored by Git.
- `data/dq_results/` - local data quality result zone, ignored by Git.
- `docs/` - active project documentation.
- `legacy/` - archived out-of-scope copied components.

## Phase 1 Foundation Components

### Faker Data Generator

`data-generator/faker_generator.py` creates synthetic banking customers, accounts, and transactions in PostgreSQL. It remains active because it supports the future governance and quality lab with realistic source data.

### PostgreSQL Source System

`postgres/schema.sql` defines the initial operational banking schema. PostgreSQL acts as the source system for later ingestion, profiling, quality checks, metadata capture, and lineage exercises.

### Docker Foundation

The active Docker Compose setup is limited to the PostgreSQL source database for Phase 1. Legacy orchestration, streaming, warehouse, and BI services are not active in this version.

## Phase 2 Run Commands

Create a local `.env` file from `.env.example` before running the source system and generator.

```powershell
docker compose up -d
Get-Content .\postgres\schema.sql | docker compose exec -T postgres psql -U banking_user -d banking
python data-generator/faker_generator.py
```

## Phase 3A Raw Ingestion

Phase 3A extracts the 10 PostgreSQL source/control tables to local raw Parquet files. Create `.env` from `.env.example` before running.

```powershell
pip install -r requirements.txt
docker compose up -d
Get-Content .\postgres\schema.sql | docker compose exec -T postgres psql -U banking_user -d banking
python data-generator/faker_generator.py
python python/ingestion/extract_postgres_to_raw.py
Get-ChildItem -Recurse data/raw
```

Optional single-table extraction:

```powershell
python python/ingestion/extract_postgres_to_raw.py --tables customers,accounts
```

### Phase 3B Validation

Phase 3B adds strict load-date validation, Parquet read-back row-count checks, and enhanced ingestion summary CSV output.

```powershell
python python/ingestion/extract_postgres_to_raw.py --tables customers --load-date 2026-06-16
python python/ingestion/extract_postgres_to_raw.py --load-date 2026-06-16
python python/ingestion/extract_postgres_to_raw.py --tables not_a_table
python python/ingestion/extract_postgres_to_raw.py --load-date 06-16-2026
Get-ChildItem .\logs\ingestion\postgres_to_raw_summary_*.csv | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Get-Content
```

## Phase 4A Raw To Standardized

Phase 4A uses PySpark to standardize raw Parquet extracts. Raw files from Phase 3 must exist before running.

```powershell
java -version
pip install -r requirements.txt
python -m py_compile spark\utils\spark_session.py spark\jobs\process_raw_to_standardized.py
python python\ingestion\extract_postgres_to_raw.py --load-date 2026-06-16
python spark\jobs\process_raw_to_standardized.py --tables customers --load-date 2026-06-16
python spark\jobs\process_raw_to_standardized.py --load-date 2026-06-16
$latestSummary = Get-ChildItem .\logs\spark\raw_to_standardized_summary_*.csv | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Import-Csv $latestSummary.FullName | Format-Table
Get-ChildItem .\data\standardized -Recurse | Select-Object -First 30
```

### Phase 4B Schema Handling

Phase 4B adds required-column checks plus schema/type normalization in the standardized Spark layer. It does not execute final data quality rules.

```powershell
python -m py_compile spark\utils\spark_session.py spark\utils\schema_config.py spark\jobs\process_raw_to_standardized.py
python spark\jobs\process_raw_to_standardized.py --load-date 2026-06-16
$latestSummary = Get-ChildItem .\logs\spark\raw_to_standardized_summary_*.csv | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Import-Csv $latestSummary.FullName | Format-Table
Get-ChildItem .\data\standardized -Recurse | Select-Object -First 30
```

## Phase 5A Curated Model Design

Phase 5A defines the curated warehouse model configuration and design documentation. It does not create curated Parquet outputs; curated output generation starts in Phase 5B.

Files added:

- `spark/utils/model_config.py`
- `docs/data_model_design.md`

Validation:

```powershell
python -m py_compile spark\utils\model_config.py
python -c "import importlib.util; spec=importlib.util.spec_from_file_location('model_config','spark/utils/model_config.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); expected={'dim_customer','dim_account','dim_branch','dim_product','fact_transaction','fact_customer_risk_score','fact_daily_account_balance'}; actual=set(m.CURATED_MODEL_CONFIGS.keys()); assert actual==expected, f'Expected {expected}, got {actual}'; print('Curated model configs validated:', sorted(actual))"
```

### Phase 5B Curated Model Build

Phase 5B builds warehouse-style dimensions and facts from standardized Parquet inputs. Outputs follow:

```text
data/curated/<model_name>/load_date=YYYY-MM-DD/<model_name>.parquet
```

```powershell
python -m py_compile spark\jobs\build_curated_models.py spark\utils\model_config.py
python spark\jobs\build_curated_models.py --models dim_customer --load-date 2026-06-16
python spark\jobs\build_curated_models.py --load-date 2026-06-16
$latestSummary = Get-ChildItem .\logs\spark\curated_model_summary_*.csv | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Import-Csv $latestSummary.FullName | Format-Table
Get-ChildItem .\data\curated -Recurse | Select-Object -First 30
```

Phase 5B performs lightweight build sanity checks only. Formal SQL data quality begins in Phase 6, and PySpark data quality begins in Phase 7.

## Phase 6A DuckDB SQL Validation

Phase 6A runs lightweight SQL data quality checks directly against curated and standardized Parquet files using in-memory DuckDB. Check results are reported but do not cause runner failure unless configuration or SQL execution fails.

```powershell
pip install -r requirements.txt
python -m py_compile python\validation\run_sql_validation.py
python python\validation\run_sql_validation.py --load-date 2026-06-16
python python\validation\run_sql_validation.py --load-date 2026-06-16 --checks 01_null_checks.sql 04_referential_integrity_checks.sql
```

Outputs:

```text
data/dq_results/sql/load_date=<load-date>/<check_name>_results.csv
logs/sql/sql_validation_summary_YYYYMMDD_HHMMSS.csv
```

### Phase 6B Reconciliation And Exceptions

Phase 6B adds source-to-target reconciliation, control totals, and bounded row-level exception evidence.

```powershell
python python\validation\run_sql_validation.py --load-date 2026-06-16
python python\validation\run_sql_validation.py --load-date 2026-06-16 --checks 05_source_target_reconciliation.sql 06_control_totals.sql 07_exception_records.sql
Get-ChildItem .\data\dq_results\sql\load_date=2026-06-16
$latestSummary = Get-ChildItem .\logs\sql\sql_validation_summary_*.csv | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Import-Csv $latestSummary.FullName | Format-Table
```

See `docs/sql_data_quality_validation.md` for the validation categories and output behavior.

## Phase 7A PySpark DQ Profiling

Phase 7A profiles curated datasets with PySpark and records schema, required-column, null, distinct-value, and duplicate-key results.

```powershell
python -m py_compile spark\dq\dq_config.py spark\dq\run_pyspark_dq_validation.py
python spark\dq\run_pyspark_dq_validation.py --load-date 2026-06-16 --datasets dim_customer
python spark\dq\run_pyspark_dq_validation.py --load-date 2026-06-16
python spark\dq\run_pyspark_dq_validation.py --load-date 2026-06-16 --datasets not_a_dataset
```

Outputs:

```text
data/dq_results/pyspark/load_date=<load-date>/
logs/dq/pyspark_dq_summary_YYYYMMDD_HHMMSS.csv
```

See `docs/pyspark_data_quality_validation.md` for profiling scope and result definitions.

### Phase 7B PySpark Rules And Exceptions

Phase 7B adds Spark accepted-value, range, referential-integrity, reconciliation, control-total, and bounded exception-record checks.

```powershell
python -m py_compile spark\dq\dq_config.py spark\dq\run_pyspark_dq_validation.py
python spark\dq\run_pyspark_dq_validation.py --load-date 2026-06-16 --datasets fact_transaction
python spark\dq\run_pyspark_dq_validation.py --load-date 2026-06-16
Get-ChildItem .\data\dq_results\pyspark\load_date=2026-06-16
$latestSummary = Get-ChildItem .\logs\dq\pyspark_dq_summary_*.csv | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Import-Csv $latestSummary.FullName | Format-Table
```

Additional outputs are `business_rule_results` and `exception_records` in CSV and Parquet formats.

## Legacy Scope

The following copied components are retained only as reference:

- `legacy/banking_dbt/`
- `legacy/consumer/`
- `legacy/kafka-debezium/`
- `legacy/airflow_dags/`
- `legacy/dockerfile-airflow.dockerfile`
- `legacy/github_workflows/`

Do not extend these components unless a future phase explicitly brings them back into scope.
