# OpenMetadata Local Runbook

## Phase 9C Purpose

Phase 9C documents a controlled approach for a possible future local
OpenMetadata run. It explains prerequisites, configuration, execution order,
validation, and troubleshooting without installing or starting OpenMetadata.

This phase is **documentation-only**. No installation, Docker modification,
service startup, ingestion execution, or metadata publication was performed.

This project uses OpenMetadata as its open-source metadata platform. It does
not use or implement Collibra.

## Future Prerequisites

Before attempting a local run:

- Obtain explicit approval for the local deployment.
- Review the current official OpenMetadata Docker and connector documentation.
- Select and pin one compatible OpenMetadata release.
- Install a supported Docker engine with Docker Compose.
- Reserve sufficient CPU, memory, and disk for the OpenMetadata application,
  metadata database, search service, and ingestion service. Current official
  quick-start guidance should be checked because requirements can change.
- Confirm the existing banking PostgreSQL service is healthy and reachable
  from the planned OpenMetadata network.
- Confirm the PostgreSQL user has metadata-read access to the `banking`
  database and `public` schema.
- Decide whether ingestion will run from the OpenMetadata UI or through an
  approved external ingestion environment.
- Review the Phase 9B templates against the schema for the selected
  OpenMetadata version.
- Back up any existing local OpenMetadata state before upgrades or resets.

Use a separate OpenMetadata deployment directory and Compose project. Do not
merge an OpenMetadata release bundle into this repository's
`docker-compose.yml`.

## Environment Variable Checklist

Supply values at runtime through an untracked environment file, shell
environment, or approved secret mechanism:

| Variable | Purpose |
| --- | --- |
| `POSTGRES_HOST` | Banking PostgreSQL host reachable by the ingestion process |
| `POSTGRES_PORT` | Banking PostgreSQL port |
| `POSTGRES_DB` | Banking source database, expected to be `banking` |
| `POSTGRES_USER` | Metadata ingestion database user |
| `POSTGRES_PASSWORD` | Runtime-only PostgreSQL credential |
| `OPENMETADATA_HOST_PORT` | OpenMetadata API endpoint |
| `OPENMETADATA_JWT_TOKEN` | Runtime-only API authentication token if required |
| `BANKING_CURATED_ROOT_PATH` | Future accessible root for curated Parquet assets |
| `OPENMETADATA_CURATED_SERVICE_TYPE` | Approved connector/service type for curated assets |
| `OPENMETADATA_LINEAGE_PUBLICATION_METHOD` | Approved manual UI or API publication method |

Do not commit resolved values, generated tokens, passwords, private keys, or
OpenMetadata deployment environment files. The Phase 9B templates contain
references only.

## Safe Execution Sequence

The commands and UI actions below are future operational steps. They were not
run in Phase 9C.

### 1. Start Existing Banking Services

From this repository, start the existing PostgreSQL pipeline services:

```powershell
docker compose up -d
docker compose ps
```

Confirm PostgreSQL is healthy and the banking schema/data are available before
attempting metadata ingestion.

### 2. Start OpenMetadata Separately

In a separate directory:

1. Download the Docker deployment files for the approved OpenMetadata release
   from the official release source.
2. Review its environment variables, image versions, ports, volumes, metadata
   database, search service, and ingestion service.
3. Start that separate Compose project using the command documented for the
   pinned release.
4. Wait until the OpenMetadata server and dependencies report healthy.
5. Open the UI endpoint documented by that release.

Do not copy unreviewed OpenMetadata services into this project's Compose file.

### 3. Configure The Banking Connection

Choose one approved method:

- **UI:** Add a PostgreSQL database service, enter runtime connection values,
  test the connection, and save it.
- **External workflow:** Resolve environment variables for
  `ingestion_configs/postgres_metadata_ingestion.yml` in an isolated,
  version-compatible ingestion environment.

Restrict discovery to the `banking` database, `public` schema, and approved
source tables. Use read-only or least-privilege access where practical.

The curated Parquet template is not directly executable until a compatible
connector or publication adapter and accessible storage location are approved.

### 4. Run Metadata Ingestion

After a successful connection test:

1. Run PostgreSQL metadata ingestion only.
2. Review workflow logs and confirm successful completion.
3. Confirm the expected source tables were created in OpenMetadata.
4. Stop and resolve unexpected schemas, tables, or connection errors before
   adding glossary, ownership, classification, curated assets, or lineage.

Do not run the Phase 9B templates unchanged unless they validate against the
selected OpenMetadata release.

### 5. Review Governance Content

Use the Phase 8 artifacts as the reviewed source material:

- Assets: `governance/catalog/data_assets.yml`
- Glossary: `governance/glossary/business_terms.yml`
- Classifications and CDEs:
  `governance/metadata/critical_data_elements.yml`
- Owners and stewards: governance YAML `owner` and `steward` fields
- Lineage: `governance/lineage/lineage_mapping.yml`
- DQ rules: `governance/data_quality/dq_rules.yml`
- DQ evidence: Phase 6 SQL and Phase 7 PySpark result outputs

Publish or enter this content only through an approved, reviewed method.
Lineage assets must exist in OpenMetadata before lineage edges are added.

## UI Validation Checklist

After a future ingestion run, verify:

- The OpenMetadata UI and API are reachable.
- The `banking_postgres` database service exists once.
- The `banking` database and `public` schema are visible.
- All ten approved PostgreSQL source tables are present.
- Table and column names match the PostgreSQL source schema.
- No unintended databases, schemas, or tables were ingested.
- Glossary terms match the Phase 8 business glossary.
- Owner and steward assignments use approved functional roles.
- PII, Confidential, Internal, and Critical Data Element classifications are
  applied consistently.
- Curated dimensions and facts, if later published, use the documented logical
  keys and grains.
- Lineage directions and field examples match the Phase 8 lineage mapping.
- DQ and profiler references do not misrepresent SQL or PySpark result files as
  OpenMetadata-executed tests.
- Search returns expected customer, account, transaction, and risk assets.
- No credentials or connection secrets are visible in descriptions or logs.

Record the selected OpenMetadata version, validation date, reviewer, and any
approved deviations outside this documentation-only phase.

## Troubleshooting

- **Insufficient resources:** Stop the deployment and increase Docker CPU,
  memory, or disk allocation according to the selected release guidance.
- **UI unavailable:** Check the separate OpenMetadata Compose project status,
  server logs, port conflicts, and dependency health.
- **Connection refused:** Verify PostgreSQL health, host/port reachability, and
  whether container networking requires a host gateway or shared network.
  `localhost` inside a container refers to that container, not necessarily the
  host banking database.
- **Authentication failure:** Recheck runtime environment values and database
  permissions without printing credentials.
- **No tables discovered:** Verify the database, `public` schema filter,
  table filter, and metadata-read privileges.
- **Workflow deployment failure:** Confirm the ingestion service is running and
  compatible with the OpenMetadata server version.
- **Template validation failure:** Compare the Phase 9B YAML with the connector
  schema for the pinned release; connector schemas can change between versions.
- **Missing lineage:** Confirm upstream and downstream assets already exist and
  their fully qualified names match the reviewed lineage template.
- **Curated Parquet unavailable:** Do not force ingestion. Approve a compatible
  connector and a storage path reachable by the ingestion process first.
- **Unexpected assets:** Stop further publication, review filters, and remove
  or correct assets only through an approved cleanup process.

Use debug logging only for troubleshooting and review logs for accidental
exposure before sharing them.

## Completion Boundary

Phase 9C ends with this runbook. It does not prove that OpenMetadata can
currently run in the local environment, and it does not authorize installation
or ingestion. A future execution requires explicit approval, a pinned release,
validated configuration, and runtime-only secrets.

## Official References

- OpenMetadata local Docker quick start:
  <https://docs.open-metadata.org/v1.12.x/quick-start/local-docker-deployment>
- OpenMetadata Docker deployment:
  <https://docs.open-metadata.org/v1.12.x/deployment/docker>
- PostgreSQL connector and external YAML workflow:
  <https://docs.open-metadata.org/v1.12.x/connectors/database/postgres/yaml>
- External ingestion framework:
  <https://docs.open-metadata.org/v1.12.x/deployment/ingestion/external>
