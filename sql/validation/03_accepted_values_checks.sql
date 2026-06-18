WITH checks AS (
    SELECT 'ACCEPTED_VALUES' AS check_category, 'account_status_accepted' AS check_name,
           'dim_account' AS table_name, 'account_status' AS column_name, 'HIGH' AS severity,
           COUNT(*) FILTER (
               WHERE account_status IS NULL
                  OR account_status NOT IN ('OPEN', 'DORMANT', 'FROZEN', 'CLOSED')
           ) AS failed_record_count,
           'Account status must be an approved source value.' AS details
    FROM dim_account
    UNION ALL
    SELECT 'ACCEPTED_VALUES', 'product_type_accepted', 'dim_product', 'product_type', 'HIGH',
           COUNT(*) FILTER (
               WHERE product_type IS NULL OR product_type NOT IN (
                   'CHECKING', 'SAVINGS', 'CREDIT_CARD', 'LOAN', 'MORTGAGE', 'INVESTMENT'
               )
           ),
           'Product type must be an approved source value.'
    FROM dim_product
    UNION ALL
    SELECT 'ACCEPTED_VALUES', 'product_status_accepted', 'dim_product', 'status', 'MEDIUM',
           COUNT(*) FILTER (
               WHERE status IS NULL OR status NOT IN ('ACTIVE', 'INACTIVE', 'RETIRED')
           ),
           'Product status must be an approved source value.'
    FROM dim_product
    UNION ALL
    SELECT 'ACCEPTED_VALUES', 'transaction_type_accepted', 'fact_transaction',
           'transaction_type', 'HIGH',
           COUNT(*) FILTER (
               WHERE transaction_type IS NULL OR transaction_type NOT IN (
                   'DEPOSIT', 'WITHDRAWAL', 'TRANSFER', 'PAYMENT', 'FEE', 'INTEREST'
               )
           ),
           'Transaction type must be an approved source value.'
    FROM fact_transaction
    UNION ALL
    SELECT 'ACCEPTED_VALUES', 'transaction_status_accepted', 'fact_transaction',
           'transaction_status', 'HIGH',
           COUNT(*) FILTER (
               WHERE transaction_status IS NULL OR transaction_status NOT IN (
                   'PENDING', 'COMPLETED', 'FAILED', 'REVERSED', 'CANCELLED'
               )
           ),
           'Transaction status must be an approved source value.'
    FROM fact_transaction
    UNION ALL
    SELECT 'ACCEPTED_VALUES', 'transaction_channel_accepted', 'fact_transaction',
           'transaction_channel', 'MEDIUM',
           COUNT(*) FILTER (
               WHERE transaction_channel IS NULL OR transaction_channel NOT IN (
                   'BRANCH', 'ATM', 'ONLINE', 'MOBILE', 'WIRE', 'ACH'
               )
           ),
           'Transaction channel must be an approved source value.'
    FROM fact_transaction
    UNION ALL
    SELECT 'ACCEPTED_VALUES', 'risk_band_accepted', 'fact_customer_risk_score',
           'risk_band', 'HIGH',
           COUNT(*) FILTER (
               WHERE risk_band IS NULL OR risk_band NOT IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
           ),
           'Risk band must be an approved source value.'
    FROM fact_customer_risk_score
    UNION ALL
    SELECT 'ACCEPTED_VALUES', 'risk_score_range', 'fact_customer_risk_score',
           'risk_score', 'HIGH',
           COUNT(*) FILTER (
               WHERE risk_score IS NULL OR risk_score < 0 OR risk_score > 1000
           ),
           'Risk score must be between 0 and 1000.'
    FROM fact_customer_risk_score
    UNION ALL
    SELECT 'ACCEPTED_VALUES', 'standardized_reference_codes_active_flag',
           'std_reference_codes', 'is_active', 'LOW',
           COUNT(*) FILTER (WHERE is_active IS NULL),
           'Reference code active flag must be populated.'
    FROM std_reference_codes
)
SELECT check_category, check_name, table_name, column_name, severity,
       failed_record_count,
       CASE WHEN failed_record_count = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       details
FROM checks
ORDER BY check_name;
