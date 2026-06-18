WITH checks AS (
    SELECT 'NULL_CHECK' AS check_category, 'dim_customer_customer_id_not_null' AS check_name,
           'dim_customer' AS table_name, 'customer_id' AS column_name, 'CRITICAL' AS severity,
           COUNT(*) FILTER (WHERE customer_id IS NULL) AS failed_record_count,
           'Customer identifiers must be populated.' AS details
    FROM dim_customer
    UNION ALL
    SELECT 'NULL_CHECK', 'dim_customer_required_fields_not_null', 'dim_customer',
           'customer_number,branch_id,email', 'HIGH',
           COUNT(*) FILTER (
               WHERE customer_number IS NULL OR branch_id IS NULL OR email IS NULL
           ),
           'Customer number, branch, and email are required.'
    FROM dim_customer
    UNION ALL
    SELECT 'NULL_CHECK', 'dim_account_required_keys_not_null', 'dim_account',
           'account_id,account_number,customer_id,product_id,branch_id', 'CRITICAL',
           COUNT(*) FILTER (
               WHERE account_id IS NULL OR account_number IS NULL OR customer_id IS NULL
                  OR product_id IS NULL OR branch_id IS NULL
           ),
           'Account and relationship keys must be populated.'
    FROM dim_account
    UNION ALL
    SELECT 'NULL_CHECK', 'dim_branch_required_fields_not_null', 'dim_branch',
           'branch_id,branch_code,branch_name', 'HIGH',
           COUNT(*) FILTER (
               WHERE branch_id IS NULL OR branch_code IS NULL OR branch_name IS NULL
           ),
           'Branch identifier, code, and name are required.'
    FROM dim_branch
    UNION ALL
    SELECT 'NULL_CHECK', 'dim_product_required_fields_not_null', 'dim_product',
           'product_id,product_code,product_name,product_type', 'HIGH',
           COUNT(*) FILTER (
               WHERE product_id IS NULL OR product_code IS NULL
                  OR product_name IS NULL OR product_type IS NULL
           ),
           'Product identifier, code, name, and type are required.'
    FROM dim_product
    UNION ALL
    SELECT 'NULL_CHECK', 'fact_transaction_required_fields_not_null', 'fact_transaction',
           'transaction_id,transaction_reference,account_id,customer_id,product_id,amount', 'CRITICAL',
           COUNT(*) FILTER (
               WHERE transaction_id IS NULL OR transaction_reference IS NULL
                  OR account_id IS NULL OR customer_id IS NULL
                  OR product_id IS NULL OR amount IS NULL
           ),
           'Transaction keys and amount must be populated.'
    FROM fact_transaction
    UNION ALL
    SELECT 'NULL_CHECK', 'fact_risk_score_required_fields_not_null', 'fact_customer_risk_score',
           'risk_score_id,customer_id,risk_score,risk_band', 'CRITICAL',
           COUNT(*) FILTER (
               WHERE risk_score_id IS NULL OR customer_id IS NULL
                  OR risk_score IS NULL OR risk_band IS NULL
           ),
           'Risk score identifiers, customer, score, and band are required.'
    FROM fact_customer_risk_score
    UNION ALL
    SELECT 'NULL_CHECK', 'fact_daily_balance_required_fields_not_null',
           'fact_daily_account_balance',
           'account_id,balance_date,customer_id,product_id,branch_id,current_balance', 'CRITICAL',
           COUNT(*) FILTER (
               WHERE account_id IS NULL OR balance_date IS NULL OR customer_id IS NULL
                  OR product_id IS NULL OR branch_id IS NULL OR current_balance IS NULL
           ),
           'Daily account balance keys and current balance are required.'
    FROM fact_daily_account_balance
)
SELECT check_category, check_name, table_name, column_name, severity,
       failed_record_count,
       CASE WHEN failed_record_count = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       details
FROM checks
ORDER BY check_name;
