# Lab 03: Lazy Evaluation, Transformations, And Actions

## Objective

Demonstrate how Spark builds a plan lazily and executes it only when an action
requires a result.

## Planned Script

`lab.py`

## Inputs

- `data/raw/customers/load_date=2026-06-16/customers.parquet`
- `data/raw/accounts/load_date=2026-06-16/accounts.parquet`

## Exercises

1. Read customers and define `select`, `filter`, `withColumn`, `trim`, `lower`,
   and `when` transformations.
2. Add print statements between transformations to prove Python continues
   without executing the complete Spark plan.
3. Trigger separate actions with `count()`, `show()`, and `collect()` on a
   bounded result.
4. Compare actions that return small results with actions that can overload the
   driver.
5. Use `explain()` before execution.
6. Identify narrow transformations in the plan.
7. Add `dropDuplicates()` and determine whether it introduces a shuffle.
8. Explain why repeated actions may recompute lineage when data is not cached.

## Questions To Answer

- What is lazy evaluation?
- Is `withColumn()` an action?
- Why does `count()` trigger work?
- Why is unrestricted `collect()` dangerous?
- What happens if two actions reuse the same uncached DataFrame?

## Deliverables

- A script showing transformations followed by actions.
- Notes classifying every operation used.
- A first-person lazy-evaluation explanation based on observed output.

## Interview Statement

> I built Spark transformation plans for banking standardization and triggered
> them only through actions such as counts and writes, which allowed Spark to
> optimize the complete execution plan.
