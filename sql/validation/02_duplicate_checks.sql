WITH checks AS (
    SELECT 'DUPLICATE_CHECK' AS check_category, 'dim_customer_primary_key_unique' AS check_name,
           'dim_customer' AS table_name, 'customer_id' AS column_name, 'CRITICAL' AS severity,
           COALESCE(SUM(row_count - 1), 0) AS failed_record_count,
           'Logical primary key customer_id must be unique.' AS details
    FROM (SELECT customer_id, COUNT(*) AS row_count FROM dim_customer GROUP BY customer_id HAVING COUNT(*) > 1)
    UNION ALL
    SELECT 'DUPLICATE_CHECK', 'dim_account_primary_key_unique', 'dim_account',
           'account_id', 'CRITICAL', COALESCE(SUM(row_count - 1), 0),
           'Logical primary key account_id must be unique.'
    FROM (SELECT account_id, COUNT(*) AS row_count FROM dim_account GROUP BY account_id HAVING COUNT(*) > 1)
    UNION ALL
    SELECT 'DUPLICATE_CHECK', 'dim_branch_primary_key_unique', 'dim_branch',
           'branch_id', 'CRITICAL', COALESCE(SUM(row_count - 1), 0),
           'Logical primary key branch_id must be unique.'
    FROM (SELECT branch_id, COUNT(*) AS row_count FROM dim_branch GROUP BY branch_id HAVING COUNT(*) > 1)
    UNION ALL
    SELECT 'DUPLICATE_CHECK', 'dim_product_primary_key_unique', 'dim_product',
           'product_id', 'CRITICAL', COALESCE(SUM(row_count - 1), 0),
           'Logical primary key product_id must be unique.'
    FROM (SELECT product_id, COUNT(*) AS row_count FROM dim_product GROUP BY product_id HAVING COUNT(*) > 1)
    UNION ALL
    SELECT 'DUPLICATE_CHECK', 'fact_transaction_primary_key_unique', 'fact_transaction',
           'transaction_id', 'CRITICAL', COALESCE(SUM(row_count - 1), 0),
           'Logical primary key transaction_id must be unique.'
    FROM (SELECT transaction_id, COUNT(*) AS row_count FROM fact_transaction GROUP BY transaction_id HAVING COUNT(*) > 1)
    UNION ALL
    SELECT 'DUPLICATE_CHECK', 'fact_risk_score_primary_key_unique', 'fact_customer_risk_score',
           'risk_score_id', 'CRITICAL', COALESCE(SUM(row_count - 1), 0),
           'Logical primary key risk_score_id must be unique.'
    FROM (SELECT risk_score_id, COUNT(*) AS row_count FROM fact_customer_risk_score GROUP BY risk_score_id HAVING COUNT(*) > 1)
    UNION ALL
    SELECT 'DUPLICATE_CHECK', 'fact_daily_balance_composite_key_unique',
           'fact_daily_account_balance', 'account_id,balance_date', 'CRITICAL',
           COALESCE(SUM(row_count - 1), 0),
           'Logical composite key account_id and balance_date must be unique.'
    FROM (
        SELECT account_id, balance_date, COUNT(*) AS row_count
        FROM fact_daily_account_balance
        GROUP BY account_id, balance_date
        HAVING COUNT(*) > 1
    )
)
SELECT check_category, check_name, table_name, column_name, severity,
       failed_record_count,
       CASE WHEN failed_record_count = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       details
FROM checks
ORDER BY check_name;
