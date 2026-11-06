# Lab 08: Catalyst, Tungsten, And Query Plans

## Objective

Explain how Spark SQL optimizes DataFrame queries and how to read logical and
physical plans.

## Planned Script

`lab.py`

## Inputs

- `fact_transaction`
- `dim_account`

## Exercises

1. Build a query that selects, filters, joins, and aggregates banking data.
2. Run `explain("extended")`.
3. Identify the parsed logical plan.
4. Identify the analyzed logical plan and resolved attributes.
5. Identify optimized-plan changes such as filter or projection pushdown.
6. Identify the physical scan, join, exchange, and aggregation operators.
7. Check for Parquet pushed filters and column pruning.
8. Compare a DataFrame expression with an equivalent Python UDF.
9. Inspect whether the UDF introduces a Python evaluation boundary.
10. Document Tungsten concepts: binary memory representation, code generation,
    reduced object overhead, and efficient CPU/memory use.

## Questions To Answer

- What does Catalyst optimize?
- What is the difference between logical and physical plans?
- What are predicate pushdown and column pruning?
- Why can Python UDFs limit optimization?
- What does Tungsten contribute?
- What is whole-stage code generation?

## Deliverables

- One annotated extended plan.
- A DataFrame-expression versus Python-UDF comparison.
- A concise Catalyst and Tungsten explanation.

## Interview Statement

> I inspected Catalyst logical and physical plans to verify filter pushdown,
> column pruning, join strategy, and shuffle behavior, while relying on
> Tungsten execution optimizations for efficient processing.
