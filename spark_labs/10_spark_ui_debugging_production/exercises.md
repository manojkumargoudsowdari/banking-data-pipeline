# Lab 10: Spark UI, Debugging, And Production Support

## Objective

Use Spark observability to diagnose execution behavior and connect technical
findings to production support.

## Planned Script

`lab.py`

## Input

Transaction and account datasets large enough to produce multiple actions and
shuffle stages.

## Exercises

1. Start an application and record the Spark UI URL.
2. Run a scan, filter, join, aggregation, and write to a lab output path.
3. Inspect the Jobs tab and map actions to jobs.
4. Inspect stage DAGs and identify shuffle boundaries.
5. Inspect task duration, input size, shuffle read/write, and locality.
6. Inspect the SQL tab and physical plans.
7. Introduce a controlled missing-column error and capture the exception.
8. Introduce a controlled invalid input path and verify clear failure handling.
9. Add structured logging for dataset, action, row count, duration, and status.
10. Write a production triage sequence from symptom to root cause.

## Questions To Answer

- Which Spark UI tabs do you inspect first?
- How do you identify a slow stage?
- What indicates skew or excessive shuffle?
- How do executor failures differ from business-rule failures?
- What information belongs in production logs?
- How do you communicate root cause and impact?

## Deliverables

- Spark UI observation notes.
- Two controlled failure examples.
- A production triage checklist.
- A first-person monitoring and support explanation.

## Interview Statement

> I monitored Spark jobs through application logs, SQL plans, stage metrics, and
> shuffle statistics to isolate data, code, and resource failures and restore
> SLA-stable processing.
