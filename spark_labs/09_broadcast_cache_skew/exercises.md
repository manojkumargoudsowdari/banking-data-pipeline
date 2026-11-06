# Lab 09: Broadcast Joins, Caching, And Skew

## Objective

Practice common Spark performance techniques and explain their tradeoffs.

## Planned Script

`lab.py`

## Inputs

- `fact_transaction`
- `dim_account`
- `dim_product`
- `dim_branch`

## Exercises

1. Measure approximate DataFrame sizes or row counts before choosing a join
   strategy.
2. Join transactions with small product and branch dimensions.
3. Compare the normal and broadcast physical plans.
4. Reuse an aggregated DataFrame in two actions without caching.
5. Cache it, materialize the cache, and rerun the actions.
6. Unpersist the DataFrame.
7. Create or identify an intentionally skewed key distribution.
8. Calculate the largest-key frequency and partition imbalance.
9. Test mitigation options such as broadcast, repartitioning, or key salting on
   lab-only data.
10. Record why caching everything is harmful.

## Questions To Answer

- When should a table be broadcast?
- What happens if a broadcast table is too large?
- When is caching useful?
- Why must cache be materialized?
- How does skew create straggler tasks?
- What evidence should justify tuning?

## Deliverables

- Join-plan comparison.
- Cached versus uncached observation.
- Skew profile and one mitigation experiment.
- A first-person performance-tuning explanation.

## Interview Statement

> I optimized Spark joins by broadcasting small banking dimensions, cached only
> reused intermediate results, and profiled key distribution before addressing
> partition skew.
