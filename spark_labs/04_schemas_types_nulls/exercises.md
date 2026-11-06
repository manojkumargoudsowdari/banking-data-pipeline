# Lab 04: Schemas, Types, Nulls, And Expressions

## Objective

Practice explicit schema reasoning, safe casting, null handling, and reusable
column expressions.

## Planned Script

`lab.py`

## Inputs

- Raw customers
- Raw accounts
- Raw transactions

## Exercises

1. Print raw schemas and compare them with `spark/utils/schema_config.py`.
2. Convert column names to lowercase snake case.
3. Trim all string fields and convert blank strings to null.
4. Lowercase email fields.
5. Uppercase status, type, code, and category fields.
6. Cast transaction amount to decimal and transaction timestamps to timestamp.
7. Create valid and invalid cast examples and observe resulting nulls.
8. Count source non-null values versus post-cast non-null values.
9. Add metadata columns for source table, load date, and processing timestamp.
10. Select columns in a stable target order.

## Questions To Answer

- Why prefer explicit schemas and types?
- What happens when a Spark cast fails?
- How is SQL null different from an empty string?
- Why should timestamps use a consistent timezone?
- When should invalid casts fail a pipeline versus become DQ evidence?

## Deliverables

- Before-and-after schemas.
- Null and cast comparison counts.
- A reusable standardization function.
- A first-person schema-normalization explanation.

## Interview Statement

> I normalized banking schemas with explicit Spark casts, controlled null
> handling, and consistent string and timestamp rules so downstream models had
> predictable data types.
