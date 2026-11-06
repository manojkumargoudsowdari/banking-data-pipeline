# Lab 11: End-To-End Banking Spark Pipeline

## Objective

Combine the previous concepts into a small, isolated banking pipeline without
modifying the project's existing outputs.

## Planned Script

`lab.py`

## Inputs

- Standardized transactions
- Standardized accounts
- Standardized customers
- Standardized products
- Standardized branches

## Exercises

1. Read all required inputs for load date `2026-06-16`.
2. Validate required columns and logical keys.
3. Build a transaction enrichment using account, customer, product, and branch
   context.
4. Apply explicit projections and aliases.
5. Create account-level transaction metrics.
6. Validate row counts before and after joins.
7. Validate critical foreign keys with anti joins.
8. Apply at least one broadcast join based on observed size.
9. Inspect the formatted physical plan.
10. Write outputs only under `labs/_outputs/lab_11/`.
11. Read outputs back and reconcile counts.
12. Produce a small execution summary.

## Questions To Answer

- What is the grain of each input and output?
- Which operations are narrow and which are wide?
- Where do shuffles occur?
- Which tables are safe broadcast candidates?
- How is data loss detected?
- What would change at production scale?

## Deliverables

- Isolated end-to-end Spark script.
- Reconciliation summary.
- Annotated physical plan.
- A two-minute project walkthrough.

## Interview Statement

> I designed an end-to-end Spark flow that enriched banking transactions,
> validated keys and counts, optimized dimension joins, and produced
> reconciled outputs for governed analytics.
