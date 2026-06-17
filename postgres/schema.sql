-- Banking Data Governance & Data Quality Pipeline
-- Phase 2B: normalized PostgreSQL banking source schema
--
-- This script is intentionally rerunnable for local practice environments.

DROP TABLE IF EXISTS source_to_target_mappings CASCADE;
DROP TABLE IF EXISTS stewardship_issues CASCADE;
DROP TABLE IF EXISTS data_quality_rules CASCADE;
DROP TABLE IF EXISTS customer_risk_scores CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS accounts CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS reference_codes CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS branches CASCADE;

CREATE TABLE branches (
    branch_id SERIAL PRIMARY KEY,
    branch_code VARCHAR(20) NOT NULL UNIQUE,
    branch_name VARCHAR(150) NOT NULL,
    branch_type VARCHAR(30) NOT NULL,
    region VARCHAR(100) NOT NULL,
    address_line1 VARCHAR(200) NOT NULL,
    address_line2 VARCHAR(200),
    city VARCHAR(100) NOT NULL,
    state_code CHAR(2) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    country_code CHAR(2) NOT NULL DEFAULT 'US',
    phone_number VARCHAR(30),
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    opened_date DATE,
    closed_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_branches_status
        CHECK (status IN ('ACTIVE', 'INACTIVE', 'CLOSED')),
    CONSTRAINT chk_branches_branch_type
        CHECK (branch_type IN ('RETAIL', 'COMMERCIAL', 'PRIVATE_BANKING', 'DIGITAL'))
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_code VARCHAR(30) NOT NULL UNIQUE,
    product_name VARCHAR(150) NOT NULL,
    product_type VARCHAR(40) NOT NULL,
    product_category VARCHAR(80) NOT NULL,
    currency CHAR(3) NOT NULL DEFAULT 'USD',
    interest_rate NUMERIC(7,4),
    monthly_fee NUMERIC(12,2) NOT NULL DEFAULT 0,
    minimum_balance NUMERIC(18,2) NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    effective_from DATE NOT NULL DEFAULT CURRENT_DATE,
    effective_to DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_products_product_type
        CHECK (product_type IN ('CHECKING', 'SAVINGS', 'CREDIT_CARD', 'LOAN', 'MORTGAGE', 'INVESTMENT')),
    CONSTRAINT chk_products_status
        CHECK (status IN ('ACTIVE', 'INACTIVE', 'RETIRED')),
    CONSTRAINT chk_products_amounts
        CHECK (monthly_fee >= 0 AND minimum_balance >= 0)
);

CREATE TABLE reference_codes (
    reference_code_id SERIAL PRIMARY KEY,
    code_domain VARCHAR(80) NOT NULL,
    code_value VARCHAR(80) NOT NULL,
    code_description VARCHAR(255) NOT NULL,
    display_order INT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    effective_from DATE NOT NULL DEFAULT CURRENT_DATE,
    effective_to DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_reference_codes_domain_value
        UNIQUE (code_domain, code_value)
);

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_number VARCHAR(30) NOT NULL UNIQUE,
    branch_id INT NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone_number VARCHAR(30),
    date_of_birth DATE,
    tax_identifier_last4 CHAR(4),
    address_line1 VARCHAR(200),
    address_line2 VARCHAR(200),
    city VARCHAR(100),
    state_code CHAR(2),
    postal_code VARCHAR(20),
    country_code CHAR(2) NOT NULL DEFAULT 'US',
    customer_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    customer_segment VARCHAR(40) NOT NULL DEFAULT 'RETAIL',
    onboarding_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_customers_branch
        FOREIGN KEY (branch_id) REFERENCES branches(branch_id),
    CONSTRAINT chk_customers_status
        CHECK (customer_status IN ('ACTIVE', 'INACTIVE', 'SUSPENDED', 'CLOSED')),
    CONSTRAINT chk_customers_segment
        CHECK (customer_segment IN ('RETAIL', 'SMALL_BUSINESS', 'COMMERCIAL', 'PRIVATE_BANKING'))
);

CREATE TABLE accounts (
    account_id SERIAL PRIMARY KEY,
    account_number VARCHAR(30) NOT NULL UNIQUE,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    branch_id INT NOT NULL,
    account_status VARCHAR(20) NOT NULL DEFAULT 'OPEN',
    current_balance NUMERIC(18,2) NOT NULL DEFAULT 0,
    available_balance NUMERIC(18,2) NOT NULL DEFAULT 0,
    currency CHAR(3) NOT NULL DEFAULT 'USD',
    opened_date DATE NOT NULL DEFAULT CURRENT_DATE,
    closed_date DATE,
    last_activity_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_accounts_customer
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_accounts_product
        FOREIGN KEY (product_id) REFERENCES products(product_id),
    CONSTRAINT fk_accounts_branch
        FOREIGN KEY (branch_id) REFERENCES branches(branch_id),
    CONSTRAINT chk_accounts_status
        CHECK (account_status IN ('OPEN', 'DORMANT', 'FROZEN', 'CLOSED')),
    CONSTRAINT chk_accounts_balances
        CHECK (current_balance >= 0 AND available_balance >= 0)
);

CREATE TABLE transactions (
    transaction_id BIGSERIAL PRIMARY KEY,
    transaction_reference VARCHAR(50) NOT NULL UNIQUE,
    account_id INT NOT NULL,
    related_account_id INT,
    branch_id INT,
    transaction_type VARCHAR(30) NOT NULL,
    transaction_channel VARCHAR(30) NOT NULL DEFAULT 'BRANCH',
    amount NUMERIC(18,2) NOT NULL,
    currency CHAR(3) NOT NULL DEFAULT 'USD',
    transaction_status VARCHAR(20) NOT NULL DEFAULT 'COMPLETED',
    description VARCHAR(255),
    merchant_name VARCHAR(150),
    transaction_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    posted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_transactions_account
        FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    CONSTRAINT fk_transactions_related_account
        FOREIGN KEY (related_account_id) REFERENCES accounts(account_id),
    CONSTRAINT fk_transactions_branch
        FOREIGN KEY (branch_id) REFERENCES branches(branch_id),
    CONSTRAINT chk_transactions_type
        CHECK (transaction_type IN ('DEPOSIT', 'WITHDRAWAL', 'TRANSFER', 'PAYMENT', 'FEE', 'INTEREST')),
    CONSTRAINT chk_transactions_channel
        CHECK (transaction_channel IN ('BRANCH', 'ATM', 'ONLINE', 'MOBILE', 'WIRE', 'ACH')),
    CONSTRAINT chk_transactions_status
        CHECK (transaction_status IN ('PENDING', 'COMPLETED', 'FAILED', 'REVERSED', 'CANCELLED')),
    CONSTRAINT chk_transactions_positive_amount
        CHECK (amount > 0)
);

CREATE TABLE customer_risk_scores (
    risk_score_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    risk_score INT NOT NULL,
    risk_band VARCHAR(20) NOT NULL,
    scoring_model VARCHAR(100) NOT NULL,
    scoring_model_version VARCHAR(30) NOT NULL,
    score_reason VARCHAR(255),
    score_date DATE NOT NULL DEFAULT CURRENT_DATE,
    effective_from DATE NOT NULL DEFAULT CURRENT_DATE,
    effective_to DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_customer_risk_scores_customer
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT chk_customer_risk_scores_score
        CHECK (risk_score BETWEEN 0 AND 1000),
    CONSTRAINT chk_customer_risk_scores_band
        CHECK (risk_band IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'))
);

CREATE TABLE data_quality_rules (
    dq_rule_id SERIAL PRIMARY KEY,
    rule_code VARCHAR(50) NOT NULL UNIQUE,
    rule_name VARCHAR(150) NOT NULL,
    rule_type VARCHAR(40) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    source_table VARCHAR(100) NOT NULL,
    source_column VARCHAR(100),
    rule_description TEXT NOT NULL,
    rule_expression TEXT,
    owner_role VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    effective_from DATE NOT NULL DEFAULT CURRENT_DATE,
    effective_to DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_data_quality_rules_type
        CHECK (rule_type IN ('NOT_NULL', 'UNIQUE', 'REFERENCE', 'RANGE', 'FORMAT', 'DOMAIN', 'RECONCILIATION')),
    CONSTRAINT chk_data_quality_rules_severity
        CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'))
);

CREATE TABLE stewardship_issues (
    issue_id SERIAL PRIMARY KEY,
    issue_reference VARCHAR(50) NOT NULL UNIQUE,
    dq_rule_id INT NOT NULL,
    source_table VARCHAR(100) NOT NULL,
    source_record_key VARCHAR(100),
    issue_status VARCHAR(30) NOT NULL DEFAULT 'OPEN',
    severity VARCHAR(20) NOT NULL,
    issue_summary VARCHAR(255) NOT NULL,
    issue_details TEXT,
    assigned_steward VARCHAR(150),
    opened_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_stewardship_issues_dq_rule
        FOREIGN KEY (dq_rule_id) REFERENCES data_quality_rules(dq_rule_id),
    CONSTRAINT chk_stewardship_issues_status
        CHECK (issue_status IN ('OPEN', 'IN_REVIEW', 'REMEDIATION', 'RESOLVED', 'CLOSED', 'REJECTED')),
    CONSTRAINT chk_stewardship_issues_severity
        CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'))
);

CREATE TABLE source_to_target_mappings (
    mapping_id SERIAL PRIMARY KEY,
    mapping_name VARCHAR(150) NOT NULL,
    source_system VARCHAR(100) NOT NULL DEFAULT 'postgres_banking_source',
    source_schema VARCHAR(100) NOT NULL DEFAULT 'public',
    source_table VARCHAR(100) NOT NULL,
    source_column VARCHAR(100) NOT NULL,
    target_layer VARCHAR(50) NOT NULL,
    target_table VARCHAR(100) NOT NULL,
    target_column VARCHAR(100) NOT NULL,
    transformation_rule TEXT,
    business_definition TEXT,
    data_owner VARCHAR(150),
    data_steward VARCHAR(150),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_source_to_target_mappings
        UNIQUE (source_system, source_schema, source_table, source_column, target_layer, target_table, target_column),
    CONSTRAINT chk_source_to_target_mappings_layer
        CHECK (target_layer IN ('RAW', 'CURATED', 'DQ_RESULTS', 'GOVERNANCE', 'WAREHOUSE'))
);

-- Foreign key indexes
CREATE INDEX idx_customers_branch_id ON customers(branch_id);

CREATE INDEX idx_accounts_customer_id ON accounts(customer_id);
CREATE INDEX idx_accounts_product_id ON accounts(product_id);
CREATE INDEX idx_accounts_branch_id ON accounts(branch_id);

CREATE INDEX idx_transactions_account_id ON transactions(account_id);
CREATE INDEX idx_transactions_related_account_id ON transactions(related_account_id);
CREATE INDEX idx_transactions_branch_id ON transactions(branch_id);

CREATE INDEX idx_customer_risk_scores_customer_id ON customer_risk_scores(customer_id);

CREATE INDEX idx_stewardship_issues_dq_rule_id ON stewardship_issues(dq_rule_id);

-- Common lookup and filtering indexes
CREATE INDEX idx_branches_branch_code ON branches(branch_code);
CREATE INDEX idx_branches_status ON branches(status);
CREATE INDEX idx_branches_region ON branches(region);

CREATE INDEX idx_products_product_code ON products(product_code);
CREATE INDEX idx_products_product_type ON products(product_type);
CREATE INDEX idx_products_status ON products(status);

CREATE INDEX idx_reference_codes_domain_value ON reference_codes(code_domain, code_value);
CREATE INDEX idx_reference_codes_active ON reference_codes(is_active);

CREATE INDEX idx_customers_customer_number ON customers(customer_number);
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_status ON customers(customer_status);
CREATE INDEX idx_customers_segment ON customers(customer_segment);

CREATE INDEX idx_accounts_account_number ON accounts(account_number);
CREATE INDEX idx_accounts_status ON accounts(account_status);
CREATE INDEX idx_accounts_opened_date ON accounts(opened_date);

CREATE INDEX idx_transactions_reference ON transactions(transaction_reference);
CREATE INDEX idx_transactions_type ON transactions(transaction_type);
CREATE INDEX idx_transactions_status ON transactions(transaction_status);
CREATE INDEX idx_transactions_transaction_at ON transactions(transaction_at);

CREATE INDEX idx_customer_risk_scores_band ON customer_risk_scores(risk_band);
CREATE INDEX idx_customer_risk_scores_score_date ON customer_risk_scores(score_date);

CREATE INDEX idx_data_quality_rules_rule_code ON data_quality_rules(rule_code);
CREATE INDEX idx_data_quality_rules_type ON data_quality_rules(rule_type);
CREATE INDEX idx_data_quality_rules_severity ON data_quality_rules(severity);
CREATE INDEX idx_data_quality_rules_source_table ON data_quality_rules(source_table);

CREATE INDEX idx_stewardship_issues_reference ON stewardship_issues(issue_reference);
CREATE INDEX idx_stewardship_issues_status ON stewardship_issues(issue_status);
CREATE INDEX idx_stewardship_issues_severity ON stewardship_issues(severity);
CREATE INDEX idx_stewardship_issues_source_record ON stewardship_issues(source_table, source_record_key);

CREATE INDEX idx_source_to_target_mappings_source ON source_to_target_mappings(source_table, source_column);
CREATE INDEX idx_source_to_target_mappings_target ON source_to_target_mappings(target_layer, target_table, target_column);
