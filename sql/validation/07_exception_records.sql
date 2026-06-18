WITH orphan_transaction_account AS (
    SELECT 'REFERENTIAL_INTEGRITY' AS exception_category,
           'orphan_fact_transaction_account' AS exception_name,
           'fact_transaction' AS table_name,
           CAST(f.transaction_id AS VARCHAR) AS business_key,
           'account_id ' || CAST(f.account_id AS VARCHAR) || ' does not exist in dim_account.' AS issue_description,
           'CRITICAL' AS severity
    FROM fact_transaction f
    LEFT JOIN dim_account a ON f.account_id = a.account_id
    WHERE f.account_id IS NOT NULL AND a.account_id IS NULL
    LIMIT 100
),
orphan_transaction_customer AS (
    SELECT 'REFERENTIAL_INTEGRITY', 'orphan_fact_transaction_customer',
           'fact_transaction', CAST(f.transaction_id AS VARCHAR),
           'customer_id ' || CAST(f.customer_id AS VARCHAR) || ' does not exist in dim_customer.',
           'CRITICAL'
    FROM fact_transaction f
    LEFT JOIN dim_customer c ON f.customer_id = c.customer_id
    WHERE f.customer_id IS NOT NULL AND c.customer_id IS NULL
    LIMIT 100
),
orphan_transaction_product AS (
    SELECT 'REFERENTIAL_INTEGRITY', 'orphan_fact_transaction_product',
           'fact_transaction', CAST(f.transaction_id AS VARCHAR),
           'product_id ' || CAST(f.product_id AS VARCHAR) || ' does not exist in dim_product.',
           'CRITICAL'
    FROM fact_transaction f
    LEFT JOIN dim_product p ON f.product_id = p.product_id
    WHERE f.product_id IS NOT NULL AND p.product_id IS NULL
    LIMIT 100
),
duplicate_transactions AS (
    SELECT 'DUPLICATE_CHECK', 'duplicate_transaction_id',
           'fact_transaction', CAST(transaction_id AS VARCHAR),
           'transaction_id occurs ' || COUNT(*) || ' times.',
           'CRITICAL'
    FROM fact_transaction
    GROUP BY transaction_id
    HAVING COUNT(*) > 1
    LIMIT 100
),
null_critical_keys AS (
    SELECT 'NULL_CHECK', 'null_critical_transaction_key',
           'fact_transaction',
           COALESCE(CAST(transaction_id AS VARCHAR), transaction_reference, '<unknown>'),
           'One or more critical transaction keys are null.',
           'CRITICAL'
    FROM fact_transaction
    WHERE transaction_id IS NULL OR transaction_reference IS NULL
       OR account_id IS NULL OR customer_id IS NULL OR product_id IS NULL
    LIMIT 100
),
invalid_transaction_amount AS (
    SELECT 'ACCEPTED_VALUES', 'invalid_transaction_amount',
           'fact_transaction', CAST(transaction_id AS VARCHAR),
           'Transaction amount must be positive; amount=' || COALESCE(CAST(amount AS VARCHAR), 'NULL'),
           'CRITICAL'
    FROM fact_transaction
    WHERE amount IS NULL OR amount <= 0
    LIMIT 100
),
missing_source_transactions AS (
    SELECT 'SOURCE_TARGET_RECONCILIATION', 'source_transaction_missing_from_fact',
           'std_transactions', CAST(s.transaction_id AS VARCHAR),
           'Source transaction_id is missing from fact_transaction.',
           'CRITICAL'
    FROM std_transactions s
    LEFT JOIN fact_transaction f ON s.transaction_id = f.transaction_id
    WHERE f.transaction_id IS NULL
    LIMIT 100
),
missing_source_accounts AS (
    SELECT 'SOURCE_TARGET_RECONCILIATION', 'source_account_missing_from_dimension',
           'std_accounts', CAST(s.account_id AS VARCHAR),
           'Source account_id is missing from dim_account.',
           'CRITICAL'
    FROM std_accounts s
    LEFT JOIN dim_account d ON s.account_id = d.account_id
    WHERE d.account_id IS NULL
    LIMIT 100
),
missing_source_customers AS (
    SELECT 'SOURCE_TARGET_RECONCILIATION', 'source_customer_missing_from_dimension',
           'std_customers', CAST(s.customer_id AS VARCHAR),
           'Source customer_id is missing from dim_customer.',
           'CRITICAL'
    FROM std_customers s
    LEFT JOIN dim_customer d ON s.customer_id = d.customer_id
    WHERE d.customer_id IS NULL
    LIMIT 100
)
SELECT * FROM orphan_transaction_account
UNION ALL SELECT * FROM orphan_transaction_customer
UNION ALL SELECT * FROM orphan_transaction_product
UNION ALL SELECT * FROM duplicate_transactions
UNION ALL SELECT * FROM null_critical_keys
UNION ALL SELECT * FROM invalid_transaction_amount
UNION ALL SELECT * FROM missing_source_transactions
UNION ALL SELECT * FROM missing_source_accounts
UNION ALL SELECT * FROM missing_source_customers;
