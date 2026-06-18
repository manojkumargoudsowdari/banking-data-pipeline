WITH checks AS (
    SELECT 'CONTROL_TOTAL' AS check_category,
           'transaction_amount_total_matches' AS check_name,
           'std_transactions,fact_transaction' AS table_name,
           'amount' AS column_name,
           'CRITICAL' AS severity,
           CASE
               WHEN COALESCE((SELECT SUM(amount) FROM std_transactions), 0)
                  = COALESCE((SELECT SUM(amount) FROM fact_transaction), 0)
               THEN 0 ELSE 1
           END AS failed_record_count,
           'Transaction amount totals must match. source='
               || COALESCE((SELECT SUM(amount) FROM std_transactions), 0)
               || ', target='
               || COALESCE((SELECT SUM(amount) FROM fact_transaction), 0) AS details
    UNION ALL
    SELECT 'CONTROL_TOTAL', 'transaction_type_counts_match',
           'std_transactions,fact_transaction', 'transaction_type', 'HIGH',
           COUNT(*),
           'Counts by transaction_type must match between standardized and curated data.'
    FROM (
        SELECT COALESCE(s.transaction_type, t.transaction_type) AS transaction_type,
               COALESCE(s.row_count, 0) AS source_count,
               COALESCE(t.row_count, 0) AS target_count
        FROM (
            SELECT transaction_type, COUNT(*) AS row_count
            FROM std_transactions
            GROUP BY transaction_type
        ) s
        FULL OUTER JOIN (
            SELECT transaction_type, COUNT(*) AS row_count
            FROM fact_transaction
            GROUP BY transaction_type
        ) t USING (transaction_type)
        WHERE COALESCE(s.row_count, 0) <> COALESCE(t.row_count, 0)
    )
    UNION ALL
    SELECT 'CONTROL_TOTAL', 'transaction_status_counts_match',
           'std_transactions,fact_transaction', 'transaction_status', 'HIGH',
           COUNT(*),
           'Counts by transaction_status must match between standardized and curated data.'
    FROM (
        SELECT COALESCE(s.transaction_status, t.transaction_status) AS transaction_status,
               COALESCE(s.row_count, 0) AS source_count,
               COALESCE(t.row_count, 0) AS target_count
        FROM (
            SELECT transaction_status, COUNT(*) AS row_count
            FROM std_transactions
            GROUP BY transaction_status
        ) s
        FULL OUTER JOIN (
            SELECT transaction_status, COUNT(*) AS row_count
            FROM fact_transaction
            GROUP BY transaction_status
        ) t USING (transaction_status)
        WHERE COALESCE(s.row_count, 0) <> COALESCE(t.row_count, 0)
    )
    UNION ALL
    SELECT 'CONTROL_TOTAL', 'account_status_counts_match',
           'std_accounts,dim_account', 'account_status', 'HIGH',
           COUNT(*),
           'Counts by account_status must match between standardized and curated data.'
    FROM (
        SELECT COALESCE(s.account_status, d.account_status) AS account_status,
               COALESCE(s.row_count, 0) AS source_count,
               COALESCE(d.row_count, 0) AS target_count
        FROM (
            SELECT account_status, COUNT(*) AS row_count
            FROM std_accounts
            GROUP BY account_status
        ) s
        FULL OUTER JOIN (
            SELECT account_status, COUNT(*) AS row_count
            FROM dim_account
            GROUP BY account_status
        ) d USING (account_status)
        WHERE COALESCE(s.row_count, 0) <> COALESCE(d.row_count, 0)
    )
    UNION ALL
    SELECT 'CONTROL_TOTAL', 'customer_branch_counts_match',
           'std_customers,dim_customer', 'branch_id', 'HIGH',
           COUNT(*),
           'Customer counts by branch_id must match between standardized and curated data.'
    FROM (
        SELECT COALESCE(s.branch_id, d.branch_id) AS branch_id,
               COALESCE(s.row_count, 0) AS source_count,
               COALESCE(d.row_count, 0) AS target_count
        FROM (
            SELECT branch_id, COUNT(*) AS row_count
            FROM std_customers
            GROUP BY branch_id
        ) s
        FULL OUTER JOIN (
            SELECT branch_id, COUNT(*) AS row_count
            FROM dim_customer
            GROUP BY branch_id
        ) d USING (branch_id)
        WHERE COALESCE(s.row_count, 0) <> COALESCE(d.row_count, 0)
    )
    UNION ALL
    SELECT 'CONTROL_TOTAL', 'current_balance_total_matches',
           'std_accounts,dim_account', 'current_balance', 'CRITICAL',
           CASE
               WHEN COALESCE((SELECT SUM(current_balance) FROM std_accounts), 0)
                  = COALESCE((SELECT SUM(current_balance) FROM dim_account), 0)
               THEN 0 ELSE 1
           END,
           'Current-balance totals must match. source='
               || COALESCE((SELECT SUM(current_balance) FROM std_accounts), 0)
               || ', target='
               || COALESCE((SELECT SUM(current_balance) FROM dim_account), 0)
    UNION ALL
    SELECT 'CONTROL_TOTAL', 'available_balance_total_matches',
           'std_accounts,dim_account', 'available_balance', 'CRITICAL',
           CASE
               WHEN COALESCE((SELECT SUM(available_balance) FROM std_accounts), 0)
                  = COALESCE((SELECT SUM(available_balance) FROM dim_account), 0)
               THEN 0 ELSE 1
           END,
           'Available-balance totals must match. source='
               || COALESCE((SELECT SUM(available_balance) FROM std_accounts), 0)
               || ', target='
               || COALESCE((SELECT SUM(available_balance) FROM dim_account), 0)
)
SELECT check_category, check_name, table_name, column_name, severity,
       failed_record_count,
       CASE WHEN failed_record_count = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       details
FROM checks
ORDER BY check_name;
