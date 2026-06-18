# Governance Foundation

## Phase 8A Purpose

Phase 8A establishes the manual governance foundation for the Banking Data
Governance & Data Quality Pipeline. The artifacts define shared business
language, governance responsibilities, critical data elements (CDEs), and
minimum expectations for data quality, lineage, stewardship, and controlled
change.

This phase adds documentation and metadata only. It does not change pipeline
logic or execute governance controls.

## Folder Structure

```text
governance/
|-- README.md
|-- governance_policy.md
|-- glossary/
|   `-- business_terms.yml
`-- metadata/
    `-- critical_data_elements.yml
```

- `governance_policy.md` defines the operating principles and accountability
  model.
- `glossary/business_terms.yml` defines the initial banking business glossary.
- `metadata/critical_data_elements.yml` maps governed fields across source,
  standardized, and curated assets.

## Future Scope

Phase 8B will extend the manual governance artifacts after review of this
foundation. It may add further ownership, classification, glossary, and
stewardship detail, but it will remain separate from pipeline execution logic.

OpenMetadata installation and metadata publication are Phase 9 activities.
Nothing in Phase 8A installs, configures, or integrates OpenMetadata.
