# Definition Of Done

## Purpose

This Definition of Done applies to governance and SDLC documentation delivered
for the Banking Data Governance & Data Quality Pipeline. It records the
completion expectations for work already implemented in Phases 6 through 10A
and does not introduce new pipeline scope.

## Governance Deliverable Checklist

- [ ] Governance policy is present and covers domains, accountability, CDEs,
      classifications, DQ, lineage, stewardship, and change control.
- [ ] Business glossary contains approved banking terms with definitions,
      domains, owners, and stewards.
- [ ] Critical Data Element inventory contains the approved CDEs and maps each
      element across source, standardized, and curated fields.
- [ ] Functional ownership and stewardship roles are documented without real
      personal names.
- [ ] Data asset catalog represents source, raw, standardized, curated, SQL DQ,
      and PySpark DQ assets.
- [ ] Source-to-target mappings cover all documented curated dimensions and
      facts.
- [ ] Lineage mapping represents source, raw, standardized, curated, SQL DQ,
      and PySpark DQ relationships.
- [ ] DQ rule catalog uses only approved implemented categories.
- [ ] Stewardship issue records are clearly marked as samples when they are not
      actual current failures.
- [ ] OpenMetadata design, templates, and local runbook are documented without
      claiming installation or execution.

## Documentation Requirements

- [ ] Documentation reflects completed repository behavior and does not invent
      unimplemented technical features.
- [ ] Business and technical terms are used consistently across artifacts.
- [ ] Paths, asset names, table names, model names, and field names match the
      repository.
- [ ] Markdown headings and checklists are readable.
- [ ] YAML files parse successfully.
- [ ] YAML structures contain the required fields and controlled values.
- [ ] Sensitive values are represented only by placeholders or environment
      variable references.
- [ ] OpenMetadata documentation states that the project uses OpenMetadata and
      does not implement Collibra.
- [ ] Screenshot references are placeholders only unless separately approved.

## Validation Requirements

- [ ] DuckDB SQL DQ evidence includes null, duplicate, accepted-value,
      referential-integrity, reconciliation, control-total, and exception
      checks.
- [ ] SQL DQ summary evidence is reviewed for execution failures and failed
      checks.
- [ ] PySpark DQ evidence includes profiling, schema, required-column,
      duplicate, accepted-value, range, referential-integrity, reconciliation,
      control-total, and exception results.
- [ ] PySpark DQ summary evidence is reviewed for dataset failures, failed
      rules, and exception counts.
- [ ] Governance YAML readability is validated.
- [ ] Agile backlog YAML readability is validated.
- [ ] Required files exist at their documented paths.
- [ ] `git diff --check` reports no whitespace errors.
- [ ] `git diff --stat` contains only the approved phase files.
- [ ] `git status --short` is clean after the approved commit.

## Review Requirements

- [ ] Data Steward reviews glossary terms, CDE mappings, classifications, and
      sample stewardship records.
- [ ] Data Quality Engineer reviews SQL and PySpark DQ evidence and confirms
      reported results align with generated summaries.
- [ ] Data Governance Lead reviews policy, ownership, catalog, lineage, and
      governance consistency.
- [ ] Data Owner reviews business meaning, material quality expectations, and
      issue disposition responsibilities.
- [ ] Platform Owner reviews OpenMetadata documentation boundaries, secret
      handling, and future deployment assumptions.
- [ ] Reviewer confirms existing Phase 10A user stories and backlog were not
      changed by Phase 10B.

## Approval Requirements

- [ ] Data Governance Lead approves governance and SDLC documentation.
- [ ] Data Owner approves business definitions and accountability assignments.
- [ ] Data Quality Engineer confirms validation evidence is accurately
      summarized.
- [ ] Platform Owner confirms that no OpenMetadata installation, Docker change,
      or ingestion execution is represented as completed.
- [ ] Git diff is reviewed before commit.
- [ ] Commit contains only the approved Phase 10B files.

Approval in this practice project means the evidence meets the documented
acceptance criteria. It does not represent legal, regulatory, production, or
enterprise change-board approval.

## Out-Of-Scope Guardrails

- [ ] No PostgreSQL schema or source data changes.
- [ ] No Python ingestion changes.
- [ ] No PySpark standardized, curated, or DQ logic changes.
- [ ] No DuckDB or SQL validation changes.
- [ ] No governance YAML or policy changes.
- [ ] No OpenMetadata documentation, template, installation, or runtime
      changes.
- [ ] No Docker or infrastructure changes.
- [ ] No data or log outputs committed.
- [ ] No requirements or dependency changes.
- [ ] No README changes.
- [ ] No changes to Phase 10A user stories or sprint backlog.
- [ ] No new technical capability is claimed by Phase 10B.
