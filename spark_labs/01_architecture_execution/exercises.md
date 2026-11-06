# Lab 01: Spark Architecture And Execution

## Objective

Explain the driver, executors, partitions, jobs, stages, tasks, DAG, and cluster
manager using an observed run from this project.

## Planned Script

`lab.py`

## Input

`data/standardized/customers/load_date=2026-06-16/customers.parquet`

## Exercises

1. Create a Spark session with application name `Lab 01 - Architecture`.
2. Print the Spark application ID, master, default parallelism, and configured
   shuffle partition count.
3. Read the customer Parquet dataset.
4. Print the DataFrame partition count.
5. Define a filter for active customers without triggering an action.
6. Print a message immediately before calling `count()`.
7. Call `count()` and observe when execution starts.
8. Add a grouped customer-status count to create a shuffle.
9. Run `explain("formatted")` and identify scan, filter, exchange, and aggregate
   operators.
10. Keep the Spark UI open long enough to inspect the Jobs, Stages, and SQL
    tabs.

## Questions To Answer

- What runs in the driver in this local application?
- What does `local[*]` mean?
- What creates a Spark job?
- Why can one job contain multiple stages?
- What normally determines the number of tasks in a stage?
- Which operation introduced an exchange or shuffle?
- How would YARN or Kubernetes change resource allocation?

## Deliverables

- Console output with application and partition information.
- One formatted physical plan.
- Notes identifying at least one action and one shuffle boundary.
- A 60-90 second first-person architecture explanation.

## Interview Statement

> I used the Spark driver to build a lazy DataFrame plan over partitioned
> banking data, triggered execution with actions, and reviewed stages and tasks
> through the physical plan and Spark UI.
