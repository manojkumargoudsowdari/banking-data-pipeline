# Lab 02: RDD, DataFrame, And Dataset

## Objective

Compare Spark's core APIs and explain why the project uses DataFrames.

## Planned Script

`lab.py`

## Input

`data/curated/dim_customer/load_date=2026-06-16/dim_customer.parquet`

## Exercises

1. Read `dim_customer` as a DataFrame.
2. Select customer ID, segment, status, and branch using DataFrame expressions.
3. Convert a small projection to an RDD and implement an equivalent filter and
   count.
4. Compare DataFrame and RDD schema awareness.
5. Print the DataFrame execution plan.
6. Explain what optimization information is lost when using arbitrary Python
   RDD functions.
7. Compare serialization, type safety, optimization, and language support.
8. Document that typed `Dataset[T]` is a Scala/Java API; PySpark exposes
   DataFrames rather than the typed Dataset API.

## Questions To Answer

- What is an RDD?
- What is a DataFrame?
- What is a typed Dataset?
- Why does Catalyst understand DataFrame expressions better than arbitrary RDD
  functions?
- When might an RDD still be appropriate?
- Why does this Python project not use typed Datasets?

## Deliverables

- Equivalent RDD and DataFrame operations.
- A comparison table covering schema, optimization, type safety, and use case.
- A first-person answer to "Why did you choose DataFrames over RDDs?"

## Interview Statement

> I used DataFrames because the banking data is structured, schema-aware, and
> suitable for Catalyst optimization, while RDDs would require more manual
> serialization and transformation logic.
