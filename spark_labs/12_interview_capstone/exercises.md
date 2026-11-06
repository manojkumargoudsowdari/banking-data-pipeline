# Lab 12: Spark Interview Capstone

## Objective

Turn observed lab evidence into clear, technically accurate interview answers.

## Planned Script

No new processing script is required unless an experiment from an earlier lab
needs to be repeated. Store answer notes in `answers.md` when this lab begins.

## Exercises

Prepare and practice answers for:

1. Explain Spark architecture to a junior developer.
2. Explain driver, executor, cluster manager, job, stage, and task.
3. Explain RDD versus DataFrame versus Dataset.
4. Explain why this project uses DataFrames.
5. Explain lazy evaluation with a project example.
6. Explain narrow versus wide transformations.
7. Explain where shuffle occurs in `fact_transaction`.
8. Explain Catalyst and Tungsten.
9. Explain broadcast joins, repartition, coalesce, cache, and skew.
10. Explain how Spark UI supports production troubleshooting.
11. Explain the PySpark DQ framework.
12. Explain one current lab limitation and the production alternative.

## Answer Rules

- Use first person.
- Begin with an action verb: built, designed, validated, optimized, or
  monitored.
- Name the actual Spark object or operation.
- State the purpose or result.
- Separate observed project behavior from hypothetical production experience.
- Keep the first answer to 60-90 seconds, then expand when asked.

## Required Evidence

Each answer must reference at least one of:

- A project file.
- A DataFrame operation.
- A physical-plan operator.
- A Spark UI observation.
- A row-count or DQ result.
- A measured partition or shuffle observation.

## Mock Follow-Ups

- What would happen with one billion transactions?
- How would this run on YARN?
- Why did Spark choose this join strategy?
- How would you detect skew?
- Why not use an RDD?
- What happens if an executor fails?
- When would you cache?
- How would you prevent small files?
- What is a limitation of the current local implementation?

## Deliverables

- Twelve practiced answers.
- Three architecture diagrams drawn from memory.
- One annotated query plan.
- One production troubleshooting walkthrough.
- One two-minute banking Spark project narrative.

## Closing Statement

> I built and validated Spark processing across standardized banking data,
> curated models, and distributed DQ checks, and I used execution plans,
> partition analysis, and runtime evidence to explain architecture and
> performance decisions.
