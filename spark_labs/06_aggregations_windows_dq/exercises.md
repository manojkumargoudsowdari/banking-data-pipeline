# Lab 06: Aggregations, Windows, And Data Quality

## Objective

Use Spark aggregations and window functions to profile banking activity and
implement explainable DQ checks.

## Planned Script

`lab.py`

## Inputs

- `fact_transaction`
- `dim_account`
- `fact_customer_risk_score`

## Exercises

1. Count transactions by type and status.
2. Calculate total, minimum, maximum, and average transaction amount.
3. Group transaction totals by account.
4. Use a window to rank transactions by amount within each account.
5. Use a window to calculate a running transaction amount by account and date.
6. Detect duplicate transaction IDs with `groupBy().count()`.
7. Check transaction amount is greater than zero.
8. Check risk score is between 0 and 1000.
9. Use a left-anti join to detect transaction account IDs missing from
   `dim_account`.
10. Produce bounded exception records with business keys and failed values.

## Questions To Answer

- How does `groupBy` affect data movement?
- What is the difference between aggregation and window calculation?
- Why does a window preserve row-level detail?
- How do anti joins support referential-integrity validation?
- Why should exceptions be bounded for review?

## Deliverables

- Aggregated banking metrics.
- Two window-function outputs.
- Duplicate, range, and referential-integrity results.
- A first-person DQ explanation.

## Interview Statement

> I used Spark aggregations, windows, and anti joins to profile banking
> transactions, validate business rules, and generate reviewable exception
> evidence.
