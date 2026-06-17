# Curated Warehouse Model Design

## Phase 5A Scope

Phase 5A defines the curated warehouse model design and configuration only. It does not create curated Parquet outputs, execute data quality rules, build OpenMetadata assets, create governance YAML files, or add Agile/JIRA artifacts.

Curated Parquet creation starts in Phase 5B.

## Modeling Approach

The curated layer uses a simple dimensional warehouse design over standardized banking data.

The standardized inputs are expected at:

```text
data/standardized/<table_name>/load_date=YYYY-MM-DD/<table_name>.parquet
```

The model design uses dimensions for descriptive business entities and facts for measured business events or snapshots. Primary and foreign keys are logical only because Parquet files do not enforce database constraints.

Formal SQL data quality checks belong to Phase 6. PySpark data quality checks belong to Phase 7.

## Model List

### dim_customer

- Model type: Dimension
- Grain: One row per customer.
- Business purpose: Customer master dimension for customer profile, segment, status, and home-branch analysis.
- Source tables: `customers`
- Logical primary key: `customer_id`
- Logical foreign keys: `branch_id` -> `dim_branch.branch_id`
- Key target columns: `customer_id`, `customer_number`, `branch_id`, `first_name`, `middle_name`, `last_name`, `email`, `phone_number`, `date_of_birth`, `customer_status`, `customer_segment`, `onboarding_date`, `source_load_date`, `standardized_at_utc`

### dim_account

- Model type: Dimension
- Grain: One row per account.
- Business purpose: Account dimension for account ownership, product assignment, branch ownership, and account status analysis.
- Source tables: `accounts`
- Logical primary key: `account_id`
- Logical foreign keys: `customer_id` -> `dim_customer.customer_id`, `product_id` -> `dim_product.product_id`, `branch_id` -> `dim_branch.branch_id`
- Key target columns: `account_id`, `account_number`, `customer_id`, `product_id`, `branch_id`, `account_status`, `current_balance`, `available_balance`, `currency`, `opened_date`, `closed_date`, `last_activity_at`, `source_load_date`, `standardized_at_utc`

### dim_branch

- Model type: Dimension
- Grain: One row per branch.
- Business purpose: Branch dimension for geography, branch type, status, and ownership analysis.
- Source tables: `branches`
- Logical primary key: `branch_id`
- Logical foreign keys: none
- Key target columns: `branch_id`, `branch_code`, `branch_name`, `branch_type`, `region`, `city`, `state_code`, `postal_code`, `country_code`, `status`, `opened_date`, `closed_date`, `source_load_date`, `standardized_at_utc`

### dim_product

- Model type: Dimension
- Grain: One row per product.
- Business purpose: Product dimension for banking product type, category, fees, balance requirements, and lifecycle analysis.
- Source tables: `products`
- Logical primary key: `product_id`
- Logical foreign keys: none
- Key target columns: `product_id`, `product_code`, `product_name`, `product_type`, `product_category`, `currency`, `interest_rate`, `monthly_fee`, `minimum_balance`, `status`, `effective_from`, `effective_to`, `source_load_date`, `standardized_at_utc`

### fact_transaction

- Model type: Fact
- Grain: One row per transaction.
- Business purpose: Transaction fact for monetary activity analysis by account, customer, branch, product, transaction type, channel, and status.
- Source tables: `transactions`, `accounts`
- Logical primary key: `transaction_id`
- Logical foreign keys: `account_id` -> `dim_account.account_id`, `customer_id` -> `dim_customer.customer_id`, `branch_id` -> `dim_branch.branch_id`, `product_id` -> `dim_product.product_id`, `related_account_id` -> `dim_account.account_id`
- Key target columns: `transaction_id`, `transaction_reference`, `account_id`, `customer_id`, `product_id`, `branch_id`, `related_account_id`, `transaction_type`, `transaction_channel`, `amount`, `currency`, `transaction_status`, `transaction_at`, `posted_at`, `source_load_date`, `standardized_at_utc`
- Notes: `customer_id` and `product_id` are sourced from standardized `accounts` by joining on `account_id` in Phase 5B.

### fact_customer_risk_score

- Model type: Fact
- Grain: One row per customer risk score record.
- Business purpose: Customer risk score fact for tracking scored risk level, risk band, model version, and effective scoring history.
- Source tables: `customer_risk_scores`
- Logical primary key: `risk_score_id`
- Logical foreign keys: `customer_id` -> `dim_customer.customer_id`
- Key target columns: `risk_score_id`, `customer_id`, `risk_score`, `risk_band`, `scoring_model`, `scoring_model_version`, `score_reason`, `score_date`, `effective_from`, `effective_to`, `source_load_date`, `standardized_at_utc`

### fact_daily_account_balance

- Model type: Fact
- Grain: One row per account per balance date.
- Business purpose: Daily account balance fact for account balance snapshot analysis by account, customer, product, branch, and load date.
- Source tables: `accounts`
- Logical primary key: `account_id`, `balance_date`
- Logical foreign keys: `account_id` -> `dim_account.account_id`, `customer_id` -> `dim_customer.customer_id`, `product_id` -> `dim_product.product_id`, `branch_id` -> `dim_branch.branch_id`
- Key target columns: `account_id`, `balance_date`, `customer_id`, `product_id`, `branch_id`, `current_balance`, `available_balance`, `currency`, `account_status`, `source_load_date`, `standardized_at_utc`
- Notes: `balance_date` is derived from the standardized `source_load_date` metadata column in Phase 5B.

## Relationship Overview

- `dim_customer.branch_id` relates customers to `dim_branch`.
- `dim_account.customer_id` relates accounts to `dim_customer`.
- `dim_account.product_id` relates accounts to `dim_product`.
- `dim_account.branch_id` relates accounts to `dim_branch`.
- `fact_transaction.account_id` relates transactions to `dim_account`.
- `fact_transaction.customer_id`, `product_id`, and `branch_id` are resolved through account and transaction relationships.
- `fact_customer_risk_score.customer_id` relates risk score records to `dim_customer`.
- `fact_daily_account_balance.account_id`, `customer_id`, `product_id`, and `branch_id` relate balance snapshots to the core dimensions.

## Constraint Note

Parquet does not enforce primary keys, foreign keys, uniqueness, or referential integrity. All keys and relationships in this design are logical and will be validated in later data quality phases.

## Phase Boundary

No curated outputs are created in Phase 5A. This phase only adds the model design document and curated model configuration.
