# SQL Data Quality Validation

## Purpose

Phase 6 provides a practical SQL validation layer for the banking pipeline. It checks standardized and curated Parquet outputs without loading them into another database.

Phase 6A established the validation runner and foundational checks. Phase 6B adds source-to-target reconciliation, control totals, and row-level exception records.

## Why DuckDB

DuckDB is used because it:

- Queries Parquet files directly.
- Runs in-process with no separate database server.
- Supports familiar analytical SQL.
- Produces portable CSV evidence for review and interview demonstrations.
- Keeps the practice lab lightweight.

## Validation Categories

### Null Checks

Verify that critical business keys and required attributes are populated.

### Duplicate Checks

Identify duplicate logical primary keys in dimensions and facts.

### Accepted Values

Validate controlled status, type, channel, and risk values against approved domains.

### Referential Integrity

Check logical relationships between facts and dimensions. Parquet does not enforce foreign keys, so these checks provide explicit evidence.

### Source-to-Target Reconciliation

Compare standardized and curated row counts and business keys to confirm that model builds did not lose or add records unexpectedly.

### Control Totals

Compare totals and grouped counts, including transaction amounts, balances, transaction classifications, account statuses, and customer branch counts.

### Exception Records

Return bounded row-level evidence for orphan keys, duplicates, null critical keys, invalid amounts, and source records missing from curated targets.

## Outputs

Per-check results:

```text
data/dq_results/sql/load_date=<load-date>/<sql_file_stem>_results.csv
```

Runtime logs and summary:

```text
logs/sql/sql_validation_YYYYMMDD_HHMMSS.log
logs/sql/sql_validation_summary_YYYYMMDD_HHMMSS.csv
```

Aggregate SQL files return PASS/FAIL check summaries. The exception SQL file returns actual exception rows. Data quality failures are reported as evidence; only runner, configuration, or SQL execution errors cause a nonzero process exit.

## Practice Value

This phase supports hands-on discussion of:

- Data quality dimensions and controls.
- Logical key validation in file-based data platforms.
- Source-to-target reconciliation.
- Control totals and balancing.
- Exception reporting and audit evidence.
- Separating validation outcomes from technical job failures.

The implementation is intentionally practical rather than a full enterprise rules engine.
