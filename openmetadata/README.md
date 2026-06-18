# OpenMetadata Integration Approach

## Phase 9A Purpose

Phase 9A defines how the Banking Data Governance & Data Quality Pipeline may
integrate with OpenMetadata. It is documentation only: no OpenMetadata service
is installed, no ingestion configuration is created, and no metadata is
published.

The design builds on the manual governance artifacts completed in Phase 8 and
provides a controlled path toward catalog, glossary, ownership, classification,
lineage, and data quality practice in a metadata platform.

## Why OpenMetadata

OpenMetadata is an open-source metadata management platform that can support
hands-on practice with concepts commonly found in enterprise governance tools:

- Business glossary management
- Data asset cataloging and discovery
- Ownership and stewardship
- Tags and classifications
- Technical lineage
- Profiling and data quality visibility

This project does **not** use or implement Collibra. OpenMetadata is used as an
open-source counterpart for practicing Collibra-style governance concepts and
workflows without claiming product equivalence or Collibra integration.

## Governance Artifact Mapping

| OpenMetadata concept | Existing project source |
| --- | --- |
| Glossary and terms | `governance/glossary/business_terms.yml` |
| Data assets | `governance/catalog/data_assets.yml` |
| Owners and stewards | `owner` and `steward` fields in governance YAML files |
| Tags and classifications | PII, Confidential, Internal, and Critical Data Element classifications |
| Lineage | `governance/lineage/lineage_mapping.yml` |
| Data quality rules | `governance/data_quality/dq_rules.yml` |
| Profiler and DQ evidence | Phase 6 SQL DQ and Phase 7 PySpark DQ outputs |

The Phase 8 files remain manual governance documentation. A later phase must
define how their values are translated into OpenMetadata entities and
relationships.

## Local Deployment Options

### Docker-Based Local Deployment

OpenMetadata can be deployed locally with its supported Docker-based setup.
This option provides the application services and web UI but adds local
resource, configuration, and version-management requirements.

No Docker or OpenMetadata installation files are added in Phase 9A.

### UI-Based Ingestion

After an approved deployment, ingestion workflows can be configured through
the OpenMetadata UI. This is suitable for interactive setup and learning the
platform's service, connection, and ingestion concepts.

### External YAML-Based Ingestion

OpenMetadata also supports externally managed YAML ingestion configurations.
This approach is preferable when configuration review, repeatability, and
version control are required. Templates may be designed in Phase 9B, but no
ingestion YAML is created in Phase 9A.

## Recommended Project Approach

1. **Phase 9A:** Document the integration approach and map existing governance
   artifacts to OpenMetadata concepts.
2. **Phase 9B:** Create reviewed ingestion configuration templates without
   exposing credentials or assuming a running OpenMetadata deployment.
3. **Phase 9C:** Optionally deploy OpenMetadata locally only after explicit
   approval and environment review.

This sequence separates governance design, configuration, and installation so
each can be reviewed independently.

## Phase 9B Configuration Templates

Phase 9B adds non-executed templates under `openmetadata/ingestion_configs/`:

- `postgres_metadata_ingestion.yml` follows the external PostgreSQL metadata
  workflow structure and uses environment-variable references only.
- `curated_layer_metadata_ingestion.yml` describes the future catalog
  representation of local curated Parquet assets. It requires an approved
  compatible connector or publication adapter before execution.
- `lineage_ingestion.yml` prepares lineage edges for future manual or API-based
  publication, using `governance/lineage/lineage_mapping.yml` as the source of
  truth.

These templates are not run in Phase 9B. OpenMetadata installation, connector
selection, credential provisioning, and metadata publication remain deferred.

## Phase 9C Local Runbook

Phase 9C adds a documentation-only local operations guide at
[`local_runbook.md`](local_runbook.md). It covers prerequisites, runtime
environment variables, a safe future execution sequence, UI validation, and
troubleshooting.

The runbook does not install or start OpenMetadata and does not authorize
ingestion. Any future local run requires explicit approval and a pinned,
reviewed OpenMetadata release.

## Phase 9A Out Of Scope

Phase 9A does not include:

- OpenMetadata installation or service startup
- Docker Compose or container changes
- UI or external ingestion execution
- Ingestion configuration YAML files
- Database, Parquet, glossary, lineage, profiler, or DQ publication
- Pipeline code changes
- Runtime outputs
- Agile artifacts

## No Secrets Policy

Credentials, tokens, passwords, private keys, and connection secrets must not
be committed to the repository or embedded in documentation or future
ingestion templates. Future configurations must use placeholders or
environment-variable references, with real values supplied through an
approved local or managed secret mechanism.
