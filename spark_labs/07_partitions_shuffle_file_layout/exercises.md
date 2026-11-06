# Lab 07: Partitions, Shuffle, And File Layout

## Objective

Separate Spark execution partitions from storage partitioning and observe how
partition choices affect tasks, shuffle, and output files.

## Planned Script

`lab.py`

## Input

`data/curated/fact_transaction/load_date=2026-06-16/fact_transaction.parquet`

## Exercises

1. Print the input DataFrame partition count.
2. Compare `repartition(2)`, `repartition(8)`, and `coalesce(1)`.
3. Inspect plans for exchange operators.
4. Write temporary outputs under `labs/_outputs/lab_07/`.
5. Count output part files for each strategy.
6. Repartition by `transaction_type` and inspect distribution.
7. Calculate row counts per partition with `mapPartitionsWithIndex`.
8. Change `spark.sql.shuffle.partitions` and compare aggregation task counts.
9. Explain the difference between `load_date=2026-06-16` storage layout and
   runtime Spark partitions.
10. Identify risks of many tiny files and one oversized partition.

## Questions To Answer

- What is a Spark partition?
- What is a storage partition?
- Does `repartition()` shuffle?
- When can `coalesce()` avoid a full shuffle?
- How do shuffle partitions affect tasks?
- What causes small-file problems?

## Deliverables

- Partition-count comparison.
- Row distribution by partition.
- Output file-count comparison.
- A first-person partition-tuning explanation.

## Interview Statement

> I analyzed execution partitions separately from load-date storage
> partitioning and tuned repartitioning and shuffle counts to balance
> parallelism, file size, and SLA stability.
