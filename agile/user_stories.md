# Agile User Stories

Phase 10A documents how the completed Banking Data Governance & Data Quality
Pipeline work could be represented in an Agile/Scrum delivery model. These
stories describe completed governance, catalog, lineage, data quality, and
OpenMetadata planning outcomes. They do not introduce new technical scope.

## Governance Epic

Story ID: GOV-001
Epic: Governance
Title: Define Banking Governance Policy
Story Points: 5

User Story:
As a Data Governance Lead, I want a banking governance policy documented so
that ownership, stewardship, classifications, data quality, lineage, and change
control expectations are clear.

Acceptance Criteria:

- Governance policy exists for the banking governance lab
- Data domains are documented
- Owner and steward responsibilities are defined
- Data quality, lineage, stewardship issue, and change control expectations are documented

Story ID: GOV-002
Epic: Governance
Title: Document Business Glossary
Story Points: 3

User Story:
As a Data Steward, I want key banking business terms documented so that project
teams use consistent definitions across source, standardized, curated, and DQ
assets.

Acceptance Criteria:

- Business glossary exists
- Customer, Account, Branch, Product, Transaction, Risk Band, and CDE terms are defined
- Each term has a domain, owner, and steward
- Definitions use functional roles rather than real names

Story ID: GOV-003
Epic: Governance
Title: Define Critical Data Elements
Story Points: 5

User Story:
As a Data Steward, I want Critical Data Elements documented so that governance
controls can be applied consistently to important banking fields.

Acceptance Criteria:

- CDE inventory exists
- CDEs map to business terms and domains
- Classifications are documented
- Source, standardized, and curated fields are mapped
- Applicable DQ rule categories are assigned

Story ID: GOV-004
Epic: Governance
Title: Assign Functional Ownership And Stewardship
Story Points: 3

User Story:
As a Data Governance Lead, I want functional owners and stewards assigned so
that accountability is clear without exposing personal names.

Acceptance Criteria:

- Owner roles are documented for governed domains
- Steward roles are documented for governed domains
- Ownership appears in glossary, CDE, DQ, catalog, and stewardship artifacts
- No real personal names are used

## Catalog Epic

Story ID: CAT-001
Epic: Catalog
Title: Catalog Banking Data Assets
Story Points: 5

User Story:
As a Metadata Administrator, I want banking data assets cataloged so that
source, raw, standardized, curated, SQL DQ, and PySpark DQ assets can be
discovered and reviewed.

Acceptance Criteria:

- Source PostgreSQL assets are listed
- Raw and standardized Parquet assets are listed
- Curated dimensions and facts are listed
- SQL and PySpark DQ result assets are listed

Story ID: CAT-002
Epic: Catalog
Title: Register Metadata For Curated Models
Story Points: 3

User Story:
As an Analytics Data Steward, I want curated model metadata documented so that
the purpose, grain, and logical keys are clear.

Acceptance Criteria:

- Curated dimensions are represented
- Curated fact models are represented
- Logical keys and grains are documented
- Asset domains are assigned

Story ID: CAT-003
Epic: Catalog
Title: Document Asset Ownership
Story Points: 3

User Story:
As a Data Governance Lead, I want catalog assets linked to owner and steward
roles so that support and accountability are visible.

Acceptance Criteria:

- Asset owners are documented by layer
- Asset stewards are documented by layer
- Functional roles are used consistently
- Ownership supports future metadata platform mapping

Story ID: CAT-004
Epic: Catalog
Title: Apply Classification Expectations
Story Points: 3

User Story:
As a Data Steward, I want classifications documented for governed data so that
sensitive banking information is handled consistently.

Acceptance Criteria:

- Internal, Confidential, Restricted, and CDE concepts are represented
- CDE classifications are documented
- Classification expectations align with the governance policy
- Classification metadata can support future OpenMetadata tagging

## Lineage Epic

Story ID: LIN-001
Epic: Lineage
Title: Document Source-To-Target Mappings
Story Points: 5

User Story:
As a Data Engineer, I want source-to-target mappings documented so that the
relationship between standardized tables and curated models is traceable.

Acceptance Criteria:

- Customer, account, branch, product, transaction, risk score, and daily balance mappings exist
- Join logic is documented where applicable
- Key mappings are documented
- Important field examples are included

Story ID: LIN-002
Epic: Lineage
Title: Document End-To-End Asset Lineage
Story Points: 5

User Story:
As a Metadata Administrator, I want end-to-end lineage documented so that users
can trace data from PostgreSQL source through DQ outputs.

Acceptance Criteria:

- PostgreSQL source lineage is represented
- Raw and standardized Parquet lineage is represented
- Curated model lineage is represented
- SQL DQ and PySpark DQ result relationships are represented

Story ID: LIN-003
Epic: Lineage
Title: Capture Field-Level Lineage Examples
Story Points: 3

User Story:
As a Data Steward, I want field-level lineage examples documented so that
critical data fields can be traced across the pipeline.

Acceptance Criteria:

- customer_id lineage is documented
- account_id lineage is documented
- transaction_id, transaction amount, and transaction date lineage are documented
- risk_score and risk_band lineage are documented

## Data Quality Epic

Story ID: DQ-001
Epic: Data Quality
Title: Document SQL Data Quality Validation
Story Points: 5

User Story:
As a Data Quality Engineer, I want SQL validation documented so that DuckDB DQ
checks can provide reviewable evidence over Parquet outputs.

Acceptance Criteria:

- Null check coverage is documented
- Duplicate key check coverage is documented
- Accepted value and referential integrity coverage are documented
- Reconciliation, control total, and exception records are documented

Story ID: DQ-002
Epic: Data Quality
Title: Document PySpark Data Quality Validation
Story Points: 5

User Story:
As a Data Quality Engineer, I want PySpark DQ validation documented so that
schema profiling, business rules, joins, aggregations, and exceptions are
reviewable at scale.

Acceptance Criteria:

- Dataset and column profiling outputs are documented
- Foundational rule checks are documented
- Business rule validation is documented
- Exception record outputs are documented

Story ID: DQ-003
Epic: Data Quality
Title: Capture DQ Evidence Outputs
Story Points: 3

User Story:
As a Data Steward, I want DQ evidence outputs documented so that quality results
can support audit, review, and issue triage.

Acceptance Criteria:

- SQL result output locations are documented
- PySpark result output locations are documented
- Summary and exception outputs are represented
- Evidence supports manual stewardship review

Story ID: DQ-004
Epic: Data Quality
Title: Define Exception Review Expectations
Story Points: 3

User Story:
As a Data Steward, I want sample exception review expectations documented so
that failed checks can be triaged consistently.

Acceptance Criteria:

- Sample stewardship issue examples exist
- Samples are clearly marked as non-actual failures
- Issue owner, steward, severity, and status are represented
- Exception review aligns with existing DQ categories

## OpenMetadata Epic

Story ID: OM-001
Epic: OpenMetadata
Title: Document OpenMetadata Integration Design
Story Points: 3

User Story:
As a Metadata Administrator, I want the OpenMetadata integration approach
documented so that the project has a clear metadata-platform direction.

Acceptance Criteria:

- OpenMetadata purpose is documented
- Project explicitly states it does not implement Collibra
- Phase 8 governance artifacts are mapped to OpenMetadata concepts
- Installation and ingestion are marked out of scope for design-only phases

Story ID: OM-002
Epic: OpenMetadata
Title: Create Metadata Ingestion Templates
Story Points: 5

User Story:
As a Metadata Administrator, I want safe ingestion templates documented so that
future OpenMetadata ingestion can be reviewed before execution.

Acceptance Criteria:

- PostgreSQL metadata ingestion template exists
- Curated layer catalog template exists
- Lineage template exists
- Templates use placeholders or environment variables only
- Templates are clearly marked as not executed

Story ID: OM-003
Epic: OpenMetadata
Title: Map Ownership And Classification Concepts
Story Points: 3

User Story:
As a Data Governance Lead, I want ownership and classification concepts mapped
to OpenMetadata so that governance roles and tags can be represented later.

Acceptance Criteria:

- Owners and stewards map to governance YAML fields
- Classifications map to Internal, Confidential, PII, and CDE concepts
- Glossary and catalog mappings are documented
- No secrets or runtime platform assumptions are introduced

Story ID: OM-004
Epic: OpenMetadata
Title: Prepare Local OpenMetadata Runbook
Story Points: 5

User Story:
As a Metadata Administrator, I want a local runbook documented so that a future
OpenMetadata deployment can be planned safely.

Acceptance Criteria:

- Prerequisites are documented
- Environment variable checklist is documented
- Safe future execution sequence is documented
- UI validation and troubleshooting notes are documented
- Runbook states that no installation or ingestion was performed
