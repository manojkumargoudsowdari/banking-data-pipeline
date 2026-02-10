# Banking Data Pipeline

An end-to-end banking data pipeline is provided in this repository for Power BI analytics. Synthetic banking data is generated in PostgreSQL, captured through Debezium and Kafka, landed in MinIO, loaded into Snowflake through Airflow, and transformed with dbt into analytics-ready models.

## What This Repository Contains

A complete analytics engineering workflow is demonstrated across ingestion, orchestration, warehouse loading, and semantic modeling.

### Pipeline Stages

1. **Data generation (PostgreSQL OLTP)**
   - Synthetic records are generated for `customers`, `accounts`, and `transactions`.
2. **CDC streaming (Debezium + Kafka)**
   - Row-level changes are captured from PostgreSQL and published into Kafka topics.
3. **Raw lake landing (Kafka consumer + MinIO)**
   - CDC events are batched and written as parquet files in MinIO.
4. **Warehouse ingestion (Airflow + Snowflake)**
   - Airflow DAGs download landed files and load Snowflake RAW tables.
5. **Modeling layer (dbt)**
   - Staging models, marts (dimensions/facts), and SCD snapshots are built.
6. **BI consumption (Power BI)**
   - Curated Snowflake models are consumed for dashboards and analysis.

---

## Repository Structure

- `data-generator/` - synthetic banking data producer.
- `postgres/schema.sql` - operational source schema.
- `kafka-debezium/` - Debezium connector setup helper.
- `consumer/` - Kafka-to-MinIO parquet writer.
- `docker/dags/` - Airflow DAGs for ingestion and dbt snapshot/run orchestration.
- `banking_dbt/` - dbt project for staging, marts, and snapshots.
- `docker-compose.yml` - local multi-service stack definition.

---

## Typical End-to-End Flow

1. Data is inserted into PostgreSQL source tables.
2. Debezium emits database changes to Kafka topics.
3. Consumer service writes topic payloads to MinIO parquet partitions.
4. Airflow loads landed objects to Snowflake RAW tables.
5. dbt transforms RAW tables to curated analytics models.
6. Power BI connects to curated Snowflake models.

---

## Quick Start (Local)

> The stack is containerized through Docker Compose.

1. Create and populate a `.env` file with credentials and connection settings used by PostgreSQL, MinIO, Airflow, Kafka consumer, and Snowflake.
2. Start infrastructure services:
   ```bash
   docker compose up -d
   ```
3. Initialize source schema in PostgreSQL using `postgres/schema.sql`.
4. Start or verify Debezium connector registration.
5. Run the data generator to produce source records.
6. Confirm parquet files are landing in MinIO.
7. Trigger/monitor Airflow DAGs for Snowflake load and dbt transformations.
8. Connect Power BI to Snowflake marts for analytics.

---

## Simple Analytics Tasks for Power BI Audience

The following beginner-friendly tasks can be performed using the curated models:

1. **Daily transaction volume trend**
   - Count transactions by day and identify peaks.
2. **Transaction mix by type**
   - Compare DEPOSIT, WITHDRAWAL, and TRANSFER distribution.
3. **Top customers by total transacted value**
   - Rank customers and visualize concentration.
4. **Account type distribution**
   - Compare SAVINGS vs CHECKING account share.
5. **Customer onboarding trend**
   - Track new customers by week/month.
6. **Average balance by customer cohort**
   - Segment customers by activity and compare balances.
7. **Transaction status monitoring**
   - Monitor status proportions and anomalies.
8. **Transfer relationship exploration**
   - Analyze transfer-linked account patterns.

---

## Notes

This repository serves as a practical reference implementation for building a modern banking analytics pipeline from data generation to BI consumption.
