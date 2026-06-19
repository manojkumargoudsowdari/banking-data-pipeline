# Test Evidence

## Evidence Scope

This document summarizes repository and local runtime evidence from completed
Phases 6, 7, 8, 9, and 10A. Phase 10B does not rerun or modify pipeline logic.
Runtime outputs remain ignored by Git and are referenced only as evidence.

Evidence load date: `2026-06-16`

## Phase 6 SQL Data Quality Evidence

Implementation:

- Runner: `python/validation/run_sql_validation.py`
- Engine: in-memory DuckDB over standardized and curated Parquet files
- SQL definitions: `sql/validation/01_null_checks.sql` through
  `sql/validation/07_exception_records.sql`

Validated categories:

- Null checks
- Duplicate checks
- Accepted-value checks
- Referential-integrity checks
- Source-to-target reconciliation
- Control totals
- Exception records

Observed full-suite evidence:

| SQL check file | Result rows | Failed checks | Execution status |
| --- | ---: | ---: | --- |
| `01_null_checks.sql` | 8 | 0 | SUCCESS |
| `02_duplicate_checks.sql` | 7 | 0 | SUCCESS |
| `03_accepted_values_checks.sql` | 9 | 0 | SUCCESS |
| `04_referential_integrity_checks.sql` | 14 | 0 | SUCCESS |
| `05_source_target_reconciliation.sql` | 9 | 0 | SUCCESS |
| `06_control_totals.sql` | 7 | 0 | SUCCESS |
| `07_exception_records.sql` | 0 | 0 | SUCCESS |
| **Full suite** | **54** | **0** | **SUCCESS** |

Evidence locations:

- Results: `data/dq_results/sql/load_date=2026-06-16/`
- Runtime summaries and logs: `logs/sql/`

The runner reports DQ failures as evidence; runner, configuration, or SQL
execution errors control process failure.

Screenshot placeholder:

> [Placeholder: SQL DQ result files and latest summary CSV showing 54 checks
> and 0 failed checks.]

## Phase 7 PySpark Data Quality Evidence

Implementation:

- Configuration: `spark/dq/dq_config.py`
- Runner: `spark/dq/run_pyspark_dq_validation.py`
- Inputs: seven curated Parquet datasets

Validated categories:

- Dataset and column profiling
- Schema expected-column checks
- Required-column checks
- Duplicate logical-key checks
- Accepted-value checks
- Range checks
- Referential-integrity checks with Spark joins
- Source-to-target reconciliation
- Control totals with Spark aggregations
- Bounded exception records

Observed full-suite evidence:

| Curated dataset | Status | Failed rules | Exception records |
| --- | --- | ---: | ---: |
| `dim_customer` | SUCCESS | 0 | 0 |
| `dim_account` | SUCCESS | 0 | 0 |
| `dim_branch` | SUCCESS | 0 | 0 |
| `dim_product` | SUCCESS | 0 | 0 |
| `fact_transaction` | SUCCESS | 0 | 0 |
| `fact_customer_risk_score` | SUCCESS | 0 | 0 |
| `fact_daily_account_balance` | SUCCESS | 0 | 0 |

Full-suite result:

- Curated datasets passed: **7 of 7**
- Failed rules: **0**
- Exception records: **0**
- Execution failures: **0**

Evidence locations:

- Results: `data/dq_results/pyspark/load_date=2026-06-16/`
- Runtime summaries and logs: `logs/dq/`
- Result sets include dataset profiles, column profiles, foundational rules,
  business rules, and exception records in CSV and Parquet formats.

Screenshot placeholder:

> [Placeholder: PySpark DQ result files and latest summary CSV showing all
> seven datasets successful and zero exception records.]

## Phase 8 Governance Evidence

Completed evidence:

- Governance policy: `governance/governance_policy.md`
- Business glossary: `governance/glossary/business_terms.yml`
- Critical Data Elements: **15 CDEs** in
  `governance/metadata/critical_data_elements.yml`
- Data asset catalog: `governance/catalog/data_assets.yml`
- Source-to-target mapping:
  `governance/metadata/source_to_target_mapping.yml`
- Lineage mapping: `governance/lineage/lineage_mapping.yml`
- DQ rule catalog: `governance/data_quality/dq_rules.yml`
- Sample stewardship issues:
  `governance/stewardship/data_quality_issues.yml`

Validation evidence:

- Governance YAML files were readable.
- Required glossary, CDE, mapping, lineage, and DQ categories were validated.
- Stewardship examples were marked as sample records, not actual failures.
- No pipeline logic was changed by the governance phases.

Screenshot placeholder:

> [Placeholder: Governance folder structure and YAML readability validation
> output.]

## Phase 9 OpenMetadata Evidence

Completed evidence:

- Integration design: `openmetadata/README.md`
- PostgreSQL metadata ingestion template:
  `openmetadata/ingestion_configs/postgres_metadata_ingestion.yml`
- Curated layer catalog template:
  `openmetadata/ingestion_configs/curated_layer_metadata_ingestion.yml`
- Lineage publication template:
  `openmetadata/ingestion_configs/lineage_ingestion.yml`
- Local runbook: `openmetadata/local_runbook.md`

Validation evidence:

- Templates use environment-variable references or placeholders.
- No passwords, tokens, or host secrets were committed.
- Templates are clearly marked as non-executed.
- No OpenMetadata installation was performed.
- No metadata ingestion was run.
- No Docker or pipeline configuration was changed.
- Documentation states that this project uses OpenMetadata, not Collibra.

Screenshot placeholder:

> [Placeholder: OpenMetadata documentation and safe template validation
> output. No OpenMetadata UI screenshot exists because no installation or
> ingestion was executed.]

## Phase 10A Agile Evidence

Completed evidence:

- User stories: `agile/user_stories.md`
- Sprint backlog: `agile/sprint_backlog.yml`
- User stories: **19**
- Sprints: **4**
- Backlog status: completed governance program

Epics represented:

- Governance
- Catalog
- Lineage
- Data Quality
- OpenMetadata

Validation evidence:

- Every story contains an ID, epic, title, story points, user story, and
  acceptance criteria.
- Every backlog story contains priority, owner, status, and story points.
- All backlog statuses are `Done`.
- Agile YAML was readable.

Screenshot placeholder:

> [Placeholder: Phase 10A user-story and sprint-backlog validation output.]

## Evidence Review Notes

- Screenshot entries are placeholders only; no image files were created.
- Local DQ outputs and logs are runtime evidence and remain ignored by Git.
- This evidence reflects the validated practice-lab run for load date
  `2026-06-16`; it is not production certification.
- Git history provides change traceability for the completed phase artifacts.
