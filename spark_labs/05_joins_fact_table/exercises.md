# Lab 05: Joins And Fact-Table Construction

## Objective

Build and analyze banking joins, including join semantics, duplicate lookup
keys, null foreign keys, shuffle, and fact-table grain.

## Planned Script

`lab.py`

## Inputs

- Standardized transactions
- Standardized accounts
- Curated customer, product, and branch dimensions

## Exercises

1. Confirm the grain and logical key of transactions and accounts.
2. Build an account lookup with account ID, customer ID, and product ID.
3. Check the account lookup for duplicate account IDs before joining.
4. Left join transactions to accounts on `account_id`.
5. Compare source and joined row counts.
6. Count unmatched account records.
7. Select the configured `fact_transaction` columns.
8. Compare inner, left, left-semi, and left-anti join results.
9. Inspect the physical plan and identify the join strategy.
10. Repeat with a broadcast hint and compare plans.

## Questions To Answer

- Why was a left join used for `fact_transaction`?
- How can duplicate lookup keys multiply fact rows?
- What is the difference between semi and anti joins?
- When is a broadcast join appropriate?
- Which joins cause shuffles?
- How do you prove that no records were lost?

## Deliverables

- Joined fact projection.
- Row-count and unmatched-key reconciliation.
- Physical plans with and without broadcast.
- A first-person join and enrichment explanation.

## Interview Statement

> I joined transactions with a deduplicated account lookup to add customer and
> product context, reconciled row counts, and used anti joins to identify
> unmatched banking records.
