# Release Notes

## Release Summary

This release represents the completed Banking Data Governance & Data Quality
Pipeline practice lab through Phase 10B. It combines PostgreSQL source data,
Python ingestion, PySpark processing, curated warehouse models, SQL and
PySpark data quality validation, manual governance artifacts, OpenMetadata
integration planning, and Agile/SDLC evidence.

Phase 10B adds documentation only. It does not change pipeline behavior,
governance metadata, OpenMetadata assets, infrastructure, or runtime outputs.

## Features Delivered

- Normalized PostgreSQL banking source model with synthetic data generation
- Python extraction from PostgreSQL to load-date-partitioned raw Parquet
- PySpark raw-to-standardized processing with schema normalization
- Curated dimensions and facts in Parquet
- DuckDB SQL validation and exception evidence
- PySpark profiling, business-rule validation, reconciliation, and exceptions
- Manual governance policy, glossary, CDE, catalog, mapping, lineage, DQ, and
  stewardship artifacts
- OpenMetadata integration design, safe templates, and local runbook
- Agile user stories, completed sprint backlog, Definition of Done, test
  evidence, and release documentation

## Governance Capabilities

- Governance policy for domains, owners, stewards, classifications, DQ,
  lineage, issue handling, and change control
- Business glossary for core banking terms
- Fifteen Critical Data Elements mapped across pipeline layers
- Functional owner and steward assignments
- Data classifications and governance expectations
- Manual DQ rule catalog
- Sample stewardship issue records clearly separated from actual DQ failures

## Data Quality Capabilities

- SQL null, duplicate, accepted-value, referential-integrity, reconciliation,
  control-total, and exception checks
- SQL full-suite evidence: 54 checks and 0 failed checks
- PySpark dataset and column profiling
- PySpark schema, required-column, duplicate, accepted-value, range,
  referential-integrity, reconciliation, and control-total checks
- PySpark evidence: all 7 curated datasets passed with 0 exception records
- CSV and Parquet result outputs with runtime summaries and logs

## Catalog Capabilities

- Catalog representation of PostgreSQL source tables
- Raw and standardized Parquet asset inventory
- Curated dimension and fact inventory
- SQL and PySpark DQ result asset inventory
- Asset domain, grain, logical key, owner, and steward documentation
- Future OpenMetadata catalog representation templates

## Lineage Capabilities

- Source-to-target mappings from standardized tables to curated models
- End-to-end lineage from PostgreSQL through raw, standardized, curated, and
  DQ result layers
- Field examples for customer, account, transaction, amount, date, risk score,
  and risk band
- Future manual or API-based OpenMetadata lineage publication design

## OpenMetadata Capabilities

- OpenMetadata integration approach mapped to Phase 8 governance artifacts
- Safe PostgreSQL metadata ingestion template
- Curated Parquet catalog representation template
- Lineage publication template
- Documentation-only local deployment runbook
- Environment-variable and placeholder-based credential policy
- Explicit boundary that OpenMetadata was not installed and ingestion was not
  executed
- Explicit statement that this project uses OpenMetadata, not Collibra

## Agile And SDLC Capabilities

- Nineteen completed user stories
- Four completed sprints covering Governance Foundation, Catalog and Lineage,
  Data Quality, and OpenMetadata
- Governance, Catalog, Lineage, Data Quality, and OpenMetadata epics
- Story points, priorities, owners, statuses, and acceptance criteria
- Definition of Done covering deliverables, validation, review, approval, and
  scope guardrails
- Test evidence linked to repository artifacts and local DQ summaries
- Version-controlled release evidence and commit history

## Stewardship Issue Tracking Workflow

The documented stewardship lifecycle is:

**Detected → Triaged → Assigned → Remediated → Validated → Closed**

### Detected

The Data Quality Engineer identifies a failed SQL or PySpark check or receives
a reported governance concern. Evidence includes the affected asset, field,
rule, load date, and bounded exception records where available.

### Triaged

The Data Steward confirms whether the record represents a valid issue,
determines the affected domain and CDEs, assesses severity, and checks for
duplicate or recurring issues.

### Assigned

The Data Steward assigns remediation to the accountable Data Owner or technical
team. The Data Governance Lead resolves ownership conflicts or cross-domain
impact. The Platform Owner is included for platform, access, or metadata-service
issues.

### Remediated

The assigned Data Owner coordinates the business or source correction. The
Data Quality Engineer or Platform Owner implements an approved technical
correction only through the appropriate delivery process.

### Validated

The Data Quality Engineer reruns the applicable validation and attaches
evidence. The Data Steward verifies that the business impact is resolved and
that related mappings, definitions, or classifications remain correct.

### Closed

The Data Steward records resolution evidence and recommends closure. The Data
Owner accepts the result, and the Data Governance Lead reviews closure for
critical, recurring, or policy-relevant issues.

Roles used by the workflow:

- Data Steward
- Data Quality Engineer
- Data Governance Lead
- Data Owner
- Platform Owner

## Release Validation Summary

| Area | Validation result |
| --- | --- |
| SQL DQ | 54 check results, 0 failed |
| PySpark DQ | 7 of 7 curated datasets successful, 0 exception records |
| Governance | Policy, glossary, 15 CDEs, catalog, mappings, lineage, DQ rules, and sample issues present |
| Governance YAML | Readable and structurally validated |
| OpenMetadata | Design, three templates, and local runbook present; no secrets or execution |
| Agile Phase 10A | 19 stories and 4 completed sprints validated |
| Phase 10B scope | Documentation only; three Agile SDLC files |

This release is a local practice-lab implementation and evidence package. It is
not a production release, regulatory certification, Collibra implementation,
or proof of an executed OpenMetadata deployment.
