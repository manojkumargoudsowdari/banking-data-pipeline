# Project Overview

The Banking Data Governance & Data Quality Pipeline is a practice lab for building a governance-first data platform around a synthetic banking source system.

## Target Architecture

```text
Faker Data Generator
  -> PostgreSQL Banking Source System
  -> Python Extraction / Ingestion Layer
  -> Raw Zone using Local Parquet or MinIO
  -> PySpark Processing Layer
  -> Curated Warehouse Layer
  -> SQL + PySpark Data Quality Layer
  -> OpenMetadata Governance Layer
  -> Stewardship / Issue Tracking / Agile Evidence Layer
```

## Phase 1 Scope

Phase 1 prepares the repository foundation only.

Active foundation components:

- Faker-based data generation.
- PostgreSQL source schema.
- Repository folder structure for later ingestion, processing, validation, governance, catalog, and Agile work.
- Documentation that reflects the governance and data quality direction.

Explicitly deferred:

- PySpark job implementation.
- OpenMetadata installation or configuration.
- Real governance artifacts.
- Data quality checks.
- SQL validation checks.
- Production orchestration or streaming.

## Legacy Components

dbt, Kafka, Debezium, Airflow, Snowflake, Power BI, and streaming-first assets are out of scope for this version. They are stored under `legacy/` for reference and should not be treated as active project components.
