# Banking Data Governance Policy

## Purpose

This policy establishes the minimum governance expectations for data produced
and used by the Banking Data Governance & Data Quality Pipeline practice lab.
It assigns accountability through functional roles and applies to source,
standardized, curated, and data quality result assets.

## Data Domains

The governed domains are:

- **Customer:** Customer identity, profile, contact, status, and segmentation.
- **Account:** Account ownership, status, balances, currency, and lifecycle.
- **Branch:** Branch identity, location, type, region, and operating status.
- **Product:** Banking product identity, classification, pricing, and status.
- **Transaction:** Financial activity, amount, timing, type, channel, and status.
- **Risk:** Customer risk scores, bands, scoring model, and effective dates.
- **Data Quality:** Rules, validation results, exceptions, and issue evidence.

Each governed asset must have one primary domain. Cross-domain assets retain
the owner of their primary business purpose and identify dependent domains.

## Owners And Stewards

Data owners are accountable for business meaning, authorized use, quality
expectations, and risk acceptance. Data stewards maintain definitions,
metadata, rule interpretation, issue triage, and evidence of resolution.

Phase 8A uses functional roles rather than individual names:

- Customer Data Owner and Customer Data Steward
- Deposit Products Owner and Account Data Steward
- Branch Operations Owner and Branch Data Steward
- Product Management Owner and Product Data Steward
- Payments Operations Owner and Transaction Data Steward
- Enterprise Risk Owner and Risk Data Steward
- Data Governance Council and Data Governance Steward

Role assignments must be reviewed whenever ownership, operating structure, or
system accountability changes.

## Critical Data Elements

A CDE is a field whose quality, protection, or consistent interpretation is
material to customer service, financial reporting, risk management, regulatory
obligations, or operational control.

Every CDE must identify:

- Business term and data domain
- Classification
- Functional owner and steward
- Source, standardized, and curated field mappings
- Related governed asset
- Applicable data quality rule categories

The approved Phase 8A CDE inventory is maintained in
`metadata/critical_data_elements.yml`.

## Data Classification

The project uses these classifications:

- **Internal:** Operational data intended for authorized internal use.
- **Confidential:** Sensitive business or financial data requiring restricted
  access and controlled distribution.
- **Restricted:** Direct or linkable customer information requiring the
  strongest access, handling, and disclosure controls.

Classification follows the most sensitive data represented by the element.
Derived assets must not receive a lower classification solely because they
were transformed or moved to another layer.

## Data Quality Expectations

CDEs must be evaluated using the applicable implemented categories:

- `null_check`
- `duplicate_key_check`
- `accepted_value_check`
- `range_check`
- `referential_integrity_check`
- `source_to_target_reconciliation`
- `control_total_check`
- `exception_record_review`

Data owners approve business thresholds and accepted values. Data stewards
review failures, confirm business impact, and maintain issue evidence. A rule
failure is not automatically a pipeline execution failure; handling depends on
severity, impact, and the approved operating procedure.

## Lineage Expectations

Lineage must describe the movement of governed fields through:

1. PostgreSQL source tables.
2. Standardized Parquet datasets.
3. Curated dimensions and facts.
4. SQL and PySpark data quality results.

Lineage records should identify source and target assets, field mappings,
transformations or derivations, load-date context, and the responsible
pipeline component. Phase 8A records manual field mappings only. Automated
lineage publication is outside this phase.

## Stewardship Issue Handling

Data quality and governance exceptions must be triaged by the assigned data
steward. Issue handling should record:

- Affected asset and CDE
- Detection source and applicable rule
- Severity and business impact
- Assigned owner and steward
- Root cause, remediation action, and target date
- Resolution evidence and closure decision

Critical issues require prompt owner notification. Recurring issues should
trigger root-cause review and may require a rule, process, or source-system
change.

## Change Control

Changes to glossary definitions, CDE mappings, classifications, ownership,
quality expectations, or lineage must:

1. Include a documented business reason and impact assessment.
2. Be reviewed by the relevant owner and steward.
3. Preserve traceability through version control.
4. Be coordinated with schema and pipeline changes when mappings are affected.
5. Update dependent documentation and validation rules in the appropriate
   implementation phase.

Emergency corrections must still be documented and reviewed retrospectively.
OpenMetadata publication and workflow automation are deferred to Phase 9 or
later.
