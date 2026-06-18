WITH checks AS (
    SELECT 'REFERENTIAL_INTEGRITY' AS check_category,
           'dim_customer_branch_exists' AS check_name,
           'dim_customer' AS table_name, 'branch_id' AS column_name, 'CRITICAL' AS severity,
           COUNT(*) AS failed_record_count,
           'Every customer branch_id must resolve to dim_branch.' AS details
    FROM dim_customer c
    LEFT JOIN dim_branch b ON c.branch_id = b.branch_id
    WHERE c.branch_id IS NOT NULL AND b.branch_id IS NULL
    UNION ALL
    SELECT 'REFERENTIAL_INTEGRITY', 'dim_account_customer_exists', 'dim_account',
           'customer_id', 'CRITICAL', COUNT(*),
           'Every account customer_id must resolve to dim_customer.'
    FROM dim_account a
    LEFT JOIN dim_customer c ON a.customer_id = c.customer_id
    WHERE a.customer_id IS NOT NULL AND c.customer_id IS NULL
    UNION ALL
    SELECT 'REFERENTIAL_INTEGRITY', 'dim_account_product_exists', 'dim_account',
           'product_id', 'CRITICAL', COUNT(*),
           'Every account product_id must resolve to dim_product.'
    FROM dim_account a
    LEFT JOIN dim_product p ON a.product_id = p.product_id
    WHERE a.product_id IS NOT NULL AND p.product_id IS NULL
    UNION ALL
    SELECT 'REFERENTIAL_INTEGRITY', 'dim_account_branch_exists', 'dim_account',
           'branch_id', 'CRITICAL', COUNT(*),
           'Every account branch_id must resolve to dim_branch.'
    FROM dim_account a
    LEFT JOIN dim_branch b ON a.branch_id = b.branch_id
    WHERE a.branch_id IS NOT NULL AND b.branch_id IS NULL
    UNION ALL
    SELECT 'REFERENTIAL_INTEGRITY', 'fact_transaction_account_exists', 'fact_transaction',
           'account_id', 'CRITICAL', COUNT(*),
           'Every transaction account_id must resolve to dim_account.'
    FROM fact_transaction f
    LEFT JOIN dim_account a ON f.account_id = a.account_id
    WHERE f.account_id IS NOT NULL AND a.account_id IS NULL
    UNION ALL
    SELECT 'REFERENTIAL_INTEGRITY', 'fact_transaction_customer_exists', 'fact_transaction',
           'customer_id', 'CRITICAL', COUNT(*),
           'Every transaction customer_id must resolve to dim_customer.'
    FROM fact_transaction f
    LEFT JOIN dim_customer c ON f.customer_id = c.customer_id
    WHERE f.customer_id IS NOT NULL AND c.customer_id IS NULL
    UNION ALL
    SELECT 'REFERENTIAL_INTEGRITY', 'fact_transaction_product_exists', 'fact_transaction',
           'product_id', 'CRITICAL', COUNT(*),
           'Every transaction product_id must resolve to dim_product.'
    FROM fact_transaction f
    LEFT JOIN dim_product p ON f.product_id = p.product_id
    WHERE f.product_id IS NOT NULL AND p.product_id IS NULL
    UNION ALL
    SELECT 'REFERENTIAL_INTEGRITY', 'fact_transaction_branch_exists_when_present',
           'fact_transaction', 'branch_id', 'HIGH', COUNT(*),
           'Non-null transaction branch_id values must resolve to dim_branch.'
    FROM fact_transaction f
    LEFT JOIN dim_branch b ON f.branch_id = b.branch_id
    WHERE f.branch_id IS NOT NULL AND b.branch_id IS NULL
    UNION ALL
    SELECT 'REFERENTIAL_INTEGRITY', 'fact_transaction_related_account_exists_when_present',
           'fact_transaction', 'related_account_id', 'HIGH', COUNT(*),
           'Non-null related_account_id values must resolve to dim_account.'
    FROM fact_transaction f
    LEFT JOIN dim_account a ON f.related_account_id = a.account_id
    WHERE f.related_account_id IS NOT NULL AND a.account_id IS NULL
    UNION ALL
    SELECT 'REFERENTIAL_INTEGRITY', 'fact_risk_score_customer_exists',
           'fact_customer_risk_score', 'customer_id', 'CRITICAL', COUNT(*),
           'Every risk score customer_id must resolve to dim_customer.'
    FROM fact_customer_risk_score f
    LEFT JOIN dim_customer c ON f.customer_id = c.customer_id
    WHERE f.customer_id IS NOT NULL AND c.customer_id IS NULL
    UNION ALL
    SELECT 'REFERENTIAL_INTEGRITY', 'fact_daily_balance_account_exists',
           'fact_daily_account_balance', 'account_id', 'CRITICAL', COUNT(*),
           'Every daily balance account_id must resolve to dim_account.'
    FROM fact_daily_account_balance f
    LEFT JOIN dim_account a ON f.account_id = a.account_id
    WHERE f.account_id IS NOT NULL AND a.account_id IS NULL
    UNION ALL
    SELECT 'REFERENTIAL_INTEGRITY', 'fact_daily_balance_customer_exists',
           'fact_daily_account_balance', 'customer_id', 'CRITICAL', COUNT(*),
           'Every daily balance customer_id must resolve to dim_customer.'
    FROM fact_daily_account_balance f
    LEFT JOIN dim_customer c ON f.customer_id = c.customer_id
    WHERE f.customer_id IS NOT NULL AND c.customer_id IS NULL
    UNION ALL
    SELECT 'REFERENTIAL_INTEGRITY', 'fact_daily_balance_product_exists',
           'fact_daily_account_balance', 'product_id', 'CRITICAL', COUNT(*),
           'Every daily balance product_id must resolve to dim_product.'
    FROM fact_daily_account_balance f
    LEFT JOIN dim_product p ON f.product_id = p.product_id
    WHERE f.product_id IS NOT NULL AND p.product_id IS NULL
    UNION ALL
    SELECT 'REFERENTIAL_INTEGRITY', 'fact_daily_balance_branch_exists',
           'fact_daily_account_balance', 'branch_id', 'CRITICAL', COUNT(*),
           'Every daily balance branch_id must resolve to dim_branch.'
    FROM fact_daily_account_balance f
    LEFT JOIN dim_branch b ON f.branch_id = b.branch_id
    WHERE f.branch_id IS NOT NULL AND b.branch_id IS NULL
)
SELECT check_category, check_name, table_name, column_name, severity,
       failed_record_count,
       CASE WHEN failed_record_count = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       details
FROM checks
ORDER BY check_name;
