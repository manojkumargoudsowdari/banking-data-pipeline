# Banking Spark Learning Labs

## Goal

These labs teach Spark through the existing Banking Data Governance Pipeline.
The learning pattern is:

```text
concept -> project data -> executable experiment -> observed plan/results -> interview answer
```

The labs use the project's real raw, standardized, and curated Parquet data.
They do not replace or modify the production-style pipeline jobs.

## Format

Use Python scripts as the primary format:

```text
labs/<lab_name>/
|-- exercises.md
`-- lab.py                 # created when the lab is implemented
```

Python scripts are preferred initially because they:

- Match how the current project runs PySpark.
- Make driver startup, actions, logs, and application termination visible.
- Are easy to compile, rerun, debug, and discuss in interviews.
- Avoid adding notebook dependencies.

An optional `notes.md` or `.ipynb` may be added later when visual exploration
provides a clear benefit.

## Prerequisites

- Java is available.
- Dependencies from `requirements.txt` are installed.
- Spark runs through `spark/utils/spark_session.py`.
- Project data exists for load date `2026-06-16`.

Useful checks:

```powershell
java -version
python -c "import pyspark; print(pyspark.__version__)"
Get-ChildItem .\data\raw
Get-ChildItem .\data\standardized
Get-ChildItem .\data\curated
```

## Lab Sequence

| Lab | Topic | Main project example |
| --- | --- | --- |
| 01 | Architecture and execution model | Read customers and observe driver, partitions, jobs, stages, and tasks |
| 02 | DataFrame, RDD, and Dataset | Compare APIs using curated customer data |
| 03 | Transformations, actions, and lazy evaluation | Standardize customer and account fields |
| 04 | Schemas, types, nulls, and expressions | Normalize transaction and customer columns |
| 05 | Joins and fact-table construction | Join transactions with accounts |
| 06 | Aggregations, windows, and DQ | Profile transactions and detect duplicate or invalid records |
| 07 | Partitions, shuffle, and file layout | Compare partition strategies and shuffle behavior |
| 08 | Catalyst, Tungsten, and query plans | Inspect parsed, optimized, and physical plans |
| 09 | Broadcast joins, caching, and skew | Tune transaction/account processing |
| 10 | Spark UI and production debugging | Diagnose jobs, stages, tasks, and failures |
| 11 | End-to-end banking Spark pipeline | Build a small standardized-to-curated flow |
| 12 | Interview explanation capstone | Explain architecture and optimization from observed evidence |

## Lab Rules

1. Read existing data; do not overwrite project pipeline outputs.
2. Write temporary lab outputs only under `labs/_outputs/`.
3. Use load date `2026-06-16` unless the exercise says otherwise.
4. Call `spark.stop()` in every completed script.
5. Record row counts, partition counts, and relevant plans.
6. Distinguish observed behavior from production recommendations.
7. End each lab with a first-person interview answer.

## Standard Script Shape

Each future `lab.py` should follow this structure:

```python
from pathlib import Path

from spark.utils.spark_session import create_spark_session


def main():
    spark = create_spark_session("Banking Spark Lab")
    try:
        # Read project data.
        # Build transformations.
        # Trigger actions.
        # Print observations.
        pass
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
```

## Interview Answer Pattern

Use:

```text
I built/designed/validated/optimized/monitored
+ technical object
+ for/across/through
+ business or operational purpose.
```

Example:

> I joined banking transactions with account reference data using Spark
> DataFrames to add customer and product context for governed reporting.

## Progress Tracking

For each lab, mark:

- [ ] Concepts reviewed
- [ ] Script implemented
- [ ] Script executed
- [ ] Output verified
- [ ] Query plan reviewed
- [ ] Interview answer practiced aloud
