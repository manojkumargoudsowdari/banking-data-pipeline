PYSPARK_DQ_CONFIGS = {
    "dim_customer": {
        "expected_columns": [
            "customer_id", "customer_number", "branch_id", "first_name", "middle_name",
            "last_name", "email", "phone_number", "date_of_birth", "tax_identifier_last4",
            "address_line1", "address_line2", "city", "state_code", "postal_code",
            "country_code", "customer_status", "customer_segment", "onboarding_date",
            "created_at", "updated_at", "source_load_date", "standardized_at_utc",
        ],
        "required_columns": [
            "customer_id", "customer_number", "branch_id", "first_name",
            "last_name", "email", "customer_status",
        ],
        "logical_key_columns": ["customer_id"],
        "profile_columns": [
            "customer_id", "customer_number", "branch_id", "email",
            "customer_status", "customer_segment",
        ],
    },
    "dim_account": {
        "expected_columns": [
            "account_id", "account_number", "customer_id", "product_id", "branch_id",
            "account_status", "current_balance", "available_balance", "currency",
            "opened_date", "closed_date", "last_activity_at", "created_at", "updated_at",
            "source_load_date", "standardized_at_utc",
        ],
        "required_columns": [
            "account_id", "account_number", "customer_id", "product_id",
            "branch_id", "account_status", "current_balance",
        ],
        "logical_key_columns": ["account_id"],
        "profile_columns": [
            "account_id", "account_number", "customer_id", "product_id",
            "branch_id", "account_status", "current_balance", "currency",
        ],
    },
    "dim_branch": {
        "expected_columns": [
            "branch_id", "branch_code", "branch_name", "branch_type", "region",
            "address_line1", "address_line2", "city", "state_code", "postal_code",
            "country_code", "phone_number", "status", "opened_date", "closed_date",
            "created_at", "updated_at", "source_load_date", "standardized_at_utc",
        ],
        "required_columns": [
            "branch_id", "branch_code", "branch_name", "branch_type", "region", "status",
        ],
        "logical_key_columns": ["branch_id"],
        "profile_columns": [
            "branch_id", "branch_code", "branch_type", "region", "status",
        ],
    },
    "dim_product": {
        "expected_columns": [
            "product_id", "product_code", "product_name", "product_type",
            "product_category", "currency", "interest_rate", "monthly_fee",
            "minimum_balance", "status", "effective_from", "effective_to",
            "created_at", "updated_at", "source_load_date", "standardized_at_utc",
        ],
        "required_columns": [
            "product_id", "product_code", "product_name", "product_type",
            "product_category", "status",
        ],
        "logical_key_columns": ["product_id"],
        "profile_columns": [
            "product_id", "product_code", "product_type", "product_category",
            "currency", "status",
        ],
    },
    "fact_transaction": {
        "expected_columns": [
            "transaction_id", "transaction_reference", "account_id", "customer_id",
            "product_id", "branch_id", "related_account_id", "transaction_type",
            "transaction_channel", "amount", "currency", "transaction_status",
            "description", "merchant_name", "transaction_at", "posted_at",
            "created_at", "source_load_date", "standardized_at_utc",
        ],
        "required_columns": [
            "transaction_id", "transaction_reference", "account_id", "customer_id",
            "product_id", "transaction_type", "amount", "transaction_status",
        ],
        "logical_key_columns": ["transaction_id"],
        "profile_columns": [
            "transaction_id", "account_id", "customer_id", "product_id",
            "branch_id", "transaction_type", "transaction_channel",
            "amount", "transaction_status",
        ],
    },
    "fact_customer_risk_score": {
        "expected_columns": [
            "risk_score_id", "customer_id", "risk_score", "risk_band",
            "scoring_model", "scoring_model_version", "score_reason", "score_date",
            "effective_from", "effective_to", "created_at", "source_load_date",
            "standardized_at_utc",
        ],
        "required_columns": [
            "risk_score_id", "customer_id", "risk_score", "risk_band",
            "scoring_model", "scoring_model_version", "score_date",
        ],
        "logical_key_columns": ["risk_score_id"],
        "profile_columns": [
            "risk_score_id", "customer_id", "risk_score", "risk_band",
            "scoring_model", "scoring_model_version",
        ],
    },
    "fact_daily_account_balance": {
        "expected_columns": [
            "account_id", "balance_date", "customer_id", "product_id", "branch_id",
            "current_balance", "available_balance", "currency", "account_status",
            "source_load_date", "standardized_at_utc",
        ],
        "required_columns": [
            "account_id", "balance_date", "customer_id", "product_id",
            "branch_id", "current_balance", "account_status",
        ],
        "logical_key_columns": ["account_id", "balance_date"],
        "profile_columns": [
            "account_id", "balance_date", "customer_id", "product_id",
            "branch_id", "current_balance", "available_balance", "account_status",
        ],
    },
}
