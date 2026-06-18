WITH metrics AS (
    SELECT
        (SELECT COUNT(*) FROM std_customers) AS std_customer_count,
        (SELECT COUNT(*) FROM dim_customer) AS dim_customer_count,
        (SELECT COUNT(*) FROM std_accounts) AS std_account_count,
        (SELECT COUNT(*) FROM dim_account) AS dim_account_count,
        (SELECT COUNT(*) FROM std_branches) AS std_branch_count,
        (SELECT COUNT(*) FROM dim_branch) AS dim_branch_count,
        (SELECT COUNT(*) FROM std_products) AS std_product_count,
        (SELECT COUNT(*) FROM dim_product) AS dim_product_count,
        (SELECT COUNT(*) FROM std_transactions) AS std_transaction_count,
        (SELECT COUNT(*) FROM fact_transaction) AS fact_transaction_count,
        (SELECT COUNT(*) FROM std_customer_risk_scores) AS std_risk_count,
        (SELECT COUNT(*) FROM fact_customer_risk_score) AS fact_risk_count
),
checks AS (
    SELECT 'SOURCE_TARGET_RECONCILIATION' AS check_category,
           'customer_row_count_reconciliation' AS check_name,
           'std_customers,dim_customer' AS table_name,
           'row_count' AS column_name,
           'CRITICAL' AS severity,
           ABS(std_customer_count - dim_customer_count) AS failed_record_count,
           'Standardized and curated customer row counts must match. source='
               || std_customer_count || ', target=' || dim_customer_count AS details
    FROM metrics
    UNION ALL
    SELECT 'SOURCE_TARGET_RECONCILIATION', 'account_row_count_reconciliation',
           'std_accounts,dim_account', 'row_count', 'CRITICAL',
           ABS(std_account_count - dim_account_count),
           'Standardized and curated account row counts must match. source='
               || std_account_count || ', target=' || dim_account_count
    FROM metrics
    UNION ALL
    SELECT 'SOURCE_TARGET_RECONCILIATION', 'branch_row_count_reconciliation',
           'std_branches,dim_branch', 'row_count', 'HIGH',
           ABS(std_branch_count - dim_branch_count),
           'Standardized and curated branch row counts must match. source='
               || std_branch_count || ', target=' || dim_branch_count
    FROM metrics
    UNION ALL
    SELECT 'SOURCE_TARGET_RECONCILIATION', 'product_row_count_reconciliation',
           'std_products,dim_product', 'row_count', 'HIGH',
           ABS(std_product_count - dim_product_count),
           'Standardized and curated product row counts must match. source='
               || std_product_count || ', target=' || dim_product_count
    FROM metrics
    UNION ALL
    SELECT 'SOURCE_TARGET_RECONCILIATION', 'transaction_row_count_reconciliation',
           'std_transactions,fact_transaction', 'row_count', 'CRITICAL',
           ABS(std_transaction_count - fact_transaction_count),
           'Standardized and curated transaction row counts must match. source='
               || std_transaction_count || ', target=' || fact_transaction_count
    FROM metrics
    UNION ALL
    SELECT 'SOURCE_TARGET_RECONCILIATION', 'risk_score_row_count_reconciliation',
           'std_customer_risk_scores,fact_customer_risk_score', 'row_count', 'HIGH',
           ABS(std_risk_count - fact_risk_count),
           'Standardized and curated risk-score row counts must match. source='
               || std_risk_count || ', target=' || fact_risk_count
    FROM metrics
    UNION ALL
    SELECT 'SOURCE_TARGET_RECONCILIATION', 'transaction_key_reconciliation',
           'std_transactions,fact_transaction', 'transaction_id', 'CRITICAL',
           (
               SELECT COUNT(*) FROM std_transactions s
               LEFT JOIN fact_transaction t ON s.transaction_id = t.transaction_id
               WHERE t.transaction_id IS NULL
           ) + (
               SELECT COUNT(*) FROM fact_transaction t
               LEFT JOIN std_transactions s ON t.transaction_id = s.transaction_id
               WHERE s.transaction_id IS NULL
           ),
           'Transaction IDs must reconcile in both source-to-target directions.'
    UNION ALL
    SELECT 'SOURCE_TARGET_RECONCILIATION', 'account_key_reconciliation',
           'std_accounts,dim_account', 'account_id', 'CRITICAL',
           (
               SELECT COUNT(*) FROM std_accounts s
               LEFT JOIN dim_account d ON s.account_id = d.account_id
               WHERE d.account_id IS NULL
           ) + (
               SELECT COUNT(*) FROM dim_account d
               LEFT JOIN std_accounts s ON d.account_id = s.account_id
               WHERE s.account_id IS NULL
           ),
           'Account IDs must reconcile in both source-to-target directions.'
    UNION ALL
    SELECT 'SOURCE_TARGET_RECONCILIATION', 'customer_key_reconciliation',
           'std_customers,dim_customer', 'customer_id', 'CRITICAL',
           (
               SELECT COUNT(*) FROM std_customers s
               LEFT JOIN dim_customer d ON s.customer_id = d.customer_id
               WHERE d.customer_id IS NULL
           ) + (
               SELECT COUNT(*) FROM dim_customer d
               LEFT JOIN std_customers s ON d.customer_id = s.customer_id
               WHERE s.customer_id IS NULL
           ),
           'Customer IDs must reconcile in both source-to-target directions.'
)
SELECT check_category, check_name, table_name, column_name, severity,
       failed_record_count,
       CASE WHEN failed_record_count = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       details
FROM checks
ORDER BY check_name;
