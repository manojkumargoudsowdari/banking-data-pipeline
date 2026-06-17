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

## Legacy Scope

The following copied components are retained only as reference:

- `legacy/banking_dbt/`
- `legacy/consumer/`
- `legacy/kafka-debezium/`
- `legacy/airflow_dags/`
- `legacy/dockerfile-airflow.dockerfile`
- `legacy/github_workflows/`

Do not extend these components unless a future phase explicitly brings them back into scope.
