# Banking Data Pipeline

This repository documents a complete end-to-end banking analytics pipeline designed to move transactional data from an operational database into analytics-ready models for BI consumption.

## End-to-End Pipeline Overview

The pipeline is built as a layered architecture where each stage has a clear role:

1. **Operational data simulation (PostgreSQL)**
   - Synthetic banking records are generated continuously.
   - Core entities include customers, accounts, and transactions.
   - PostgreSQL acts as the OLTP source system.

2. **Change Data Capture (Debezium + Kafka)**
   - Debezium monitors PostgreSQL write-ahead logs and captures inserts/updates/deletes.
   - Captured changes are emitted as events into Kafka topics.
   - Kafka provides durable event transport and decouples producers from downstream consumers.

3. **Streaming landing to object storage (Kafka Consumer + MinIO)**
   - A Kafka consumer service reads CDC events from topic streams.
   - Events are grouped into micro-batches and serialized as Parquet.
   - Parquet files are written into MinIO in table-based folder paths.

4. **Orchestrated warehouse ingestion (Airflow + Snowflake)**
   - Airflow coordinates scheduled ingestion tasks.
   - DAG tasks fetch staged Parquet files from MinIO.
   - Data is loaded into Snowflake RAW-layer tables for downstream transformation.

5. **Analytics transformation layer (dbt)**
   - dbt models standardize and transform RAW data into curated analytical structures.
   - The project includes:
     - **staging** models for source-aligned cleaning and normalization,
     - **marts** for business-facing fact and dimension outputs,
     - **snapshots** for historical tracking of changing records.

6. **Business intelligence consumption (Power BI)**
   - Power BI connects to Snowflake curated models.
   - Fact/dimension outputs support dashboarding, KPI analysis, and reporting workflows.

---

## Detailed Data Flow

### 1) Data creation at the source
- Data generator services create realistic banking activity patterns.
- Records are committed into PostgreSQL tables representing customer lifecycle and financial activity.

### 2) CDC event production
- Debezium connector captures row-level changes from PostgreSQL.
- Each change is published to Kafka with event metadata and operation type.

### 3) Event consumption and file conversion
- Consumer service subscribes to Kafka topics.
- Incoming JSON CDC messages are transformed and batched.
- Batches are converted into columnar Parquet format.
- Files are persisted to MinIO as the landing zone.

### 4) Workflow orchestration and loading
- Airflow DAGs handle file retrieval and warehouse load sequencing.
- Loaded data is persisted to Snowflake RAW tables to preserve ingestion fidelity.

### 5) Data modeling for analytics
- dbt applies SQL-based transformations to generate analytics-ready tables.
- Business entities are shaped into dimensions and facts for self-service BI.
- Snapshot logic preserves point-in-time history for changing attributes.

### 6) BI delivery
- Power BI consumes modeled Snowflake outputs.
- Reports can analyze customer behavior, account activity, and transaction trends.

---

## Repository Structure

- `data-generator/` — synthetic data generation logic for PostgreSQL source tables.
- `kafka-debezium/` — connector and streaming setup for CDC.
- `consumer/` — Kafka consumer that writes Parquet files to MinIO.
- `docker/` and `docker-compose.yml` — local multi-service orchestration.
- `banking_dbt/` — dbt project with staging, marts, snapshots, and sources.
- `postgres/` — PostgreSQL initialization/config artifacts.

---

## Technology Stack

- **Database (OLTP):** PostgreSQL
- **CDC:** Debezium
- **Message Broker:** Kafka
- **Object Storage:** MinIO
- **Orchestration:** Apache Airflow
- **Cloud Data Warehouse:** Snowflake
- **Transformation Framework:** dbt
- **BI Layer:** Power BI
- **Local Runtime:** Docker Compose

---

## Pipeline Outcome

This pipeline provides a complete path from operational event generation to analytics consumption:

- transactional source data is captured in near real time,
- landed as structured files,
- ingested into a cloud warehouse,
- transformed into analytical models,
- and exposed to BI dashboards for decision support.
