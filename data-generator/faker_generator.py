import os
import random
import sys
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_DOWN

import psycopg2
from dotenv import load_dotenv
from faker import Faker

load_dotenv()

fake = Faker("en_US")
Faker.seed(42)
random.seed(42)

NUM_BRANCHES = 10
NUM_PRODUCTS = 6
NUM_CUSTOMERS = 500
NUM_TRANSACTIONS = 5000
NUM_DQ_RULES = 12
NUM_STEWARDSHIP_ISSUES = 8
NUM_MAPPINGS = 25

CURRENCY = "USD"

BRANCH_TYPES = ["RETAIL", "COMMERCIAL", "PRIVATE_BANKING", "DIGITAL"]
BRANCH_STATUSES = ["ACTIVE", "INACTIVE", "CLOSED"]

PRODUCT_TYPES = ["CHECKING", "SAVINGS", "CREDIT_CARD", "LOAN", "MORTGAGE", "INVESTMENT"]
PRODUCT_STATUSES = ["ACTIVE", "INACTIVE", "RETIRED"]

CUSTOMER_STATUSES = ["ACTIVE", "INACTIVE", "SUSPENDED", "CLOSED"]
CUSTOMER_SEGMENTS = ["RETAIL", "SMALL_BUSINESS", "COMMERCIAL", "PRIVATE_BANKING"]

ACCOUNT_STATUSES = ["OPEN", "DORMANT", "FROZEN", "CLOSED"]

TRANSACTION_TYPES = ["DEPOSIT", "WITHDRAWAL", "TRANSFER", "PAYMENT", "FEE", "INTEREST"]
TRANSACTION_CHANNELS = ["BRANCH", "ATM", "ONLINE", "MOBILE", "WIRE", "ACH"]
TRANSACTION_STATUSES = ["PENDING", "COMPLETED", "FAILED", "REVERSED", "CANCELLED"]

RISK_BANDS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

DQ_RULE_TYPES = ["NOT_NULL", "UNIQUE", "REFERENCE", "RANGE", "FORMAT", "DOMAIN", "RECONCILIATION"]
SEVERITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
ISSUE_STATUSES = ["OPEN", "IN_REVIEW", "REMEDIATION", "RESOLVED", "CLOSED", "REJECTED"]
TARGET_LAYERS = ["RAW", "CURATED", "DQ_RESULTS", "GOVERNANCE", "WAREHOUSE"]


def random_money(min_val, max_val):
    value = Decimal(str(random.uniform(float(min_val), float(max_val))))
    return value.quantize(Decimal("0.01"), rounding=ROUND_DOWN)


def random_timestamp(days_back=365):
    return datetime.now(timezone.utc) - timedelta(
        days=random.randint(0, days_back),
        seconds=random.randint(0, 86400),
    )


def risk_band_for_score(score):
    if score <= 299:
        return "LOW"
    if score <= 599:
        return "MEDIUM"
    if score <= 799:
        return "HIGH"
    return "CRITICAL"


def print_count(cur, table_name):
    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cur.fetchone()[0]
    print(f"{table_name}: {count} rows")
    return count


def clear_existing_data(cur):
    tables = [
        "source_to_target_mappings",
        "stewardship_issues",
        "data_quality_rules",
        "customer_risk_scores",
        "transactions",
        "accounts",
        "customers",
        "reference_codes",
        "products",
        "branches",
    ]
    cur.execute(f"TRUNCATE TABLE {', '.join(tables)} RESTART IDENTITY CASCADE")
    print("Existing rows cleared.")


def load_reference_codes(cur):
    domains = {
        "branch_status": BRANCH_STATUSES,
        "branch_type": BRANCH_TYPES,
        "product_type": PRODUCT_TYPES,
        "product_status": PRODUCT_STATUSES,
        "customer_status": CUSTOMER_STATUSES,
        "customer_segment": CUSTOMER_SEGMENTS,
        "account_status": ACCOUNT_STATUSES,
        "transaction_type": TRANSACTION_TYPES,
        "transaction_channel": TRANSACTION_CHANNELS,
        "transaction_status": TRANSACTION_STATUSES,
        "currency": [CURRENCY],
        "risk_band": RISK_BANDS,
        "dq_rule_type": DQ_RULE_TYPES,
        "severity": SEVERITIES,
        "issue_status": ISSUE_STATUSES,
        "target_layer": TARGET_LAYERS,
    }

    for domain, values in domains.items():
        for display_order, value in enumerate(values, start=1):
            cur.execute(
                """
                INSERT INTO reference_codes (
                    code_domain,
                    code_value,
                    code_description,
                    display_order
                )
                VALUES (%s, %s, %s, %s)
                """,
                (domain, value, value.replace("_", " ").title(), display_order),
            )

    return print_count(cur, "reference_codes")


def load_branches(cur):
    branches = []
    regions = ["Northeast", "Southeast", "Midwest", "Southwest", "West"]

    for idx in range(1, NUM_BRANCHES + 1):
        branch_code = f"BR{idx:03d}"
        status = "ACTIVE" if idx <= 8 else random.choice(["INACTIVE", "CLOSED"])
        opened_date = fake.date_between(start_date="-20y", end_date="-1y")
        closed_date = fake.date_between(start_date=opened_date, end_date="today") if status == "CLOSED" else None
        cur.execute(
            """
            INSERT INTO branches (
                branch_code,
                branch_name,
                branch_type,
                region,
                address_line1,
                address_line2,
                city,
                state_code,
                postal_code,
                country_code,
                phone_number,
                status,
                opened_date,
                closed_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING branch_id, branch_code
            """,
            (
                branch_code,
                f"{fake.city()} Banking Center",
                random.choice(BRANCH_TYPES),
                random.choice(regions),
                fake.street_address(),
                fake.secondary_address() if random.random() < 0.25 else None,
                fake.city(),
                fake.state_abbr(),
                fake.postcode(),
                "US",
                fake.phone_number()[:30],
                status,
                opened_date,
                closed_date,
            ),
        )
        branches.append(cur.fetchone())

    print_count(cur, "branches")
    return branches


def load_products(cur):
    product_templates = [
        ("PROD001", "Everyday Checking", "CHECKING", "Deposit Account", Decimal("0.0000"), Decimal("5.00"), Decimal("25.00")),
        ("PROD002", "Premier Savings", "SAVINGS", "Deposit Account", Decimal("2.2500"), Decimal("0.00"), Decimal("100.00")),
        ("PROD003", "Rewards Credit Card", "CREDIT_CARD", "Credit Product", Decimal("19.9900"), Decimal("0.00"), Decimal("0.00")),
        ("PROD004", "Personal Loan", "LOAN", "Lending Product", Decimal("8.7500"), Decimal("0.00"), Decimal("0.00")),
        ("PROD005", "Home Mortgage", "MORTGAGE", "Lending Product", Decimal("6.5000"), Decimal("0.00"), Decimal("0.00")),
        ("PROD006", "Managed Investment", "INVESTMENT", "Wealth Product", Decimal("0.0000"), Decimal("15.00"), Decimal("1000.00")),
    ]

    products = []
    for code, name, product_type, category, rate, fee, minimum_balance in product_templates:
        cur.execute(
            """
            INSERT INTO products (
                product_code,
                product_name,
                product_type,
                product_category,
                currency,
                interest_rate,
                monthly_fee,
                minimum_balance,
                status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING product_id, product_code, product_type
            """,
            (
                code,
                name,
                product_type,
                category,
                CURRENCY,
                rate,
                fee,
                minimum_balance,
                random.choices(PRODUCT_STATUSES, weights=[85, 10, 5], k=1)[0],
            ),
        )
        products.append(cur.fetchone())

    print_count(cur, "products")
    return products


def load_customers(cur, branches):
    customers = []

    for idx in range(1, NUM_CUSTOMERS + 1):
        branch_id = random.choice(branches)[0]
        status = random.choices(CUSTOMER_STATUSES, weights=[88, 7, 3, 2], k=1)[0]
        first_name = fake.first_name()
        last_name = fake.last_name()
        cur.execute(
            """
            INSERT INTO customers (
                customer_number,
                branch_id,
                first_name,
                middle_name,
                last_name,
                email,
                phone_number,
                date_of_birth,
                tax_identifier_last4,
                address_line1,
                address_line2,
                city,
                state_code,
                postal_code,
                country_code,
                customer_status,
                customer_segment,
                onboarding_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING customer_id, customer_number, branch_id
            """,
            (
                f"CUST{idx:06d}",
                branch_id,
                first_name,
                fake.first_name() if random.random() < 0.2 else None,
                last_name,
                f"cust{idx:06d}.{first_name.lower()}.{last_name.lower()}@examplebank.test",
                fake.phone_number()[:30],
                fake.date_of_birth(minimum_age=18, maximum_age=90),
                f"{random.randint(0, 9999):04d}",
                fake.street_address(),
                fake.secondary_address() if random.random() < 0.2 else None,
                fake.city(),
                fake.state_abbr(),
                fake.postcode(),
                "US",
                status,
                random.choices(CUSTOMER_SEGMENTS, weights=[75, 12, 8, 5], k=1)[0],
                fake.date_between(start_date="-10y", end_date="today"),
            ),
        )
        customers.append(cur.fetchone())

    print_count(cur, "customers")
    return customers


def load_accounts(cur, customers, products, branches):
    accounts = []
    account_idx = 0

    for customer_id, _customer_number, customer_branch_id in customers:
        for _ in range(random.randint(1, 3)):
            account_idx += 1
            product_id, _product_code, _product_type = random.choice(products)
            branch_id = customer_branch_id if random.random() < 0.8 else random.choice(branches)[0]
            current_balance = random_money(Decimal("0.00"), Decimal("250000.00"))
            available_balance = random_money(Decimal("0.00"), current_balance)
            status = random.choices(ACCOUNT_STATUSES, weights=[85, 7, 3, 5], k=1)[0]
            opened_date = fake.date_between(start_date="-10y", end_date="today")
            closed_date = fake.date_between(start_date=opened_date, end_date="today") if status == "CLOSED" else None
            cur.execute(
                """
                INSERT INTO accounts (
                    account_number,
                    customer_id,
                    product_id,
                    branch_id,
                    account_status,
                    current_balance,
                    available_balance,
                    currency,
                    opened_date,
                    closed_date,
                    last_activity_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING account_id, account_number, customer_id, branch_id
                """,
                (
                    f"ACCT{account_idx:06d}",
                    customer_id,
                    product_id,
                    branch_id,
                    status,
                    current_balance,
                    available_balance,
                    CURRENCY,
                    opened_date,
                    closed_date,
                    random_timestamp(120),
                ),
            )
            accounts.append(cur.fetchone())

    print_count(cur, "accounts")
    return accounts


def load_transactions(cur, accounts, branches):
    for idx in range(1, NUM_TRANSACTIONS + 1):
        account_id, _account_number, _customer_id, account_branch_id = random.choice(accounts)
        transaction_type = random.choices(
            TRANSACTION_TYPES,
            weights=[25, 18, 16, 22, 7, 12],
            k=1,
        )[0]
        related_account_id = None
        if transaction_type == "TRANSFER":
            related_candidates = [account for account in accounts if account[0] != account_id]
            related_account_id = random.choice(related_candidates)[0]

        branch_id = account_branch_id if random.random() < 0.65 else random.choice(branches)[0]
        channel = random.choice(TRANSACTION_CHANNELS)
        if channel in ["ONLINE", "MOBILE", "ACH"] and random.random() < 0.65:
            branch_id = None

        transaction_at = random_timestamp(365)
        status = random.choices(TRANSACTION_STATUSES, weights=[8, 84, 4, 3, 1], k=1)[0]
        posted_at = transaction_at + timedelta(days=random.randint(0, 2)) if status == "COMPLETED" else None

        cur.execute(
            """
            INSERT INTO transactions (
                transaction_reference,
                account_id,
                related_account_id,
                branch_id,
                transaction_type,
                transaction_channel,
                amount,
                currency,
                transaction_status,
                description,
                merchant_name,
                transaction_at,
                posted_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                f"TXN{idx:09d}",
                account_id,
                related_account_id,
                branch_id,
                transaction_type,
                channel,
                random_money(Decimal("1.00"), Decimal("10000.00")),
                CURRENCY,
                status,
                f"{transaction_type.title()} transaction",
                fake.company() if transaction_type in ["PAYMENT", "FEE"] else None,
                transaction_at,
                posted_at,
            ),
        )

    return print_count(cur, "transactions")


def load_customer_risk_scores(cur, customers):
    for customer_id, _customer_number, _branch_id in customers:
        for score_number in range(random.randint(1, 2)):
            score = random.randint(0, 1000)
            score_date = date.today() - timedelta(days=random.randint(0, 365))
            cur.execute(
                """
                INSERT INTO customer_risk_scores (
                    customer_id,
                    risk_score,
                    risk_band,
                    scoring_model,
                    scoring_model_version,
                    score_reason,
                    score_date,
                    effective_from,
                    effective_to
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    customer_id,
                    score,
                    risk_band_for_score(score),
                    "Banking Customer Risk Model",
                    "v1.0",
                    random.choice([
                        "Payment behavior",
                        "Account age",
                        "Transaction activity",
                        "Customer profile review",
                    ]),
                    score_date,
                    score_date,
                    None if score_number == 0 else score_date + timedelta(days=180),
                ),
            )

    return print_count(cur, "customer_risk_scores")


def load_data_quality_rules(cur):
    rule_templates = [
        ("DQ_RULE_001", "Customer number is required", "NOT_NULL", "CRITICAL", "customers", "customer_number"),
        ("DQ_RULE_002", "Customer email is unique", "UNIQUE", "HIGH", "customers", "email"),
        ("DQ_RULE_003", "Customer branch exists", "REFERENCE", "CRITICAL", "customers", "branch_id"),
        ("DQ_RULE_004", "Account number is required", "NOT_NULL", "CRITICAL", "accounts", "account_number"),
        ("DQ_RULE_005", "Account customer exists", "REFERENCE", "CRITICAL", "accounts", "customer_id"),
        ("DQ_RULE_006", "Account balance is nonnegative", "RANGE", "HIGH", "accounts", "current_balance"),
        ("DQ_RULE_007", "Transaction reference is unique", "UNIQUE", "HIGH", "transactions", "transaction_reference"),
        ("DQ_RULE_008", "Transaction amount is positive", "RANGE", "CRITICAL", "transactions", "amount"),
        ("DQ_RULE_009", "Transaction type is controlled", "DOMAIN", "MEDIUM", "transactions", "transaction_type"),
        ("DQ_RULE_010", "Risk score is in range", "RANGE", "HIGH", "customer_risk_scores", "risk_score"),
        ("DQ_RULE_011", "Risk band is controlled", "DOMAIN", "MEDIUM", "customer_risk_scores", "risk_band"),
        ("DQ_RULE_012", "Mapping source column is required", "NOT_NULL", "MEDIUM", "source_to_target_mappings", "source_column"),
    ]

    rules = []
    for rule_code, rule_name, rule_type, severity, source_table, source_column in rule_templates[:NUM_DQ_RULES]:
        cur.execute(
            """
            INSERT INTO data_quality_rules (
                rule_code,
                rule_name,
                rule_type,
                severity,
                source_table,
                source_column,
                rule_description,
                rule_expression,
                owner_role
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING dq_rule_id, rule_code, severity, source_table, source_column
            """,
            (
                rule_code,
                rule_name,
                rule_type,
                severity,
                source_table,
                source_column,
                f"Validates that {source_table}.{source_column or '*'} satisfies {rule_name.lower()}.",
                f"{source_column} validation rule" if source_column else "table-level validation rule",
                random.choice(["Data Steward", "Data Governance Lead", "Data Engineering"]),
            ),
        )
        rules.append(cur.fetchone())

    print_count(cur, "data_quality_rules")
    return rules


def load_stewardship_issues(cur, dq_rules):
    for idx in range(1, NUM_STEWARDSHIP_ISSUES + 1):
        dq_rule_id, _rule_code, severity, source_table, source_column = random.choice(dq_rules)
        status = random.choices(ISSUE_STATUSES, weights=[30, 20, 15, 20, 10, 5], k=1)[0]
        opened_at = random_timestamp(45)
        resolved_at = opened_at + timedelta(days=random.randint(1, 14)) if status in ["RESOLVED", "CLOSED"] else None
        cur.execute(
            """
            INSERT INTO stewardship_issues (
                issue_reference,
                dq_rule_id,
                source_table,
                source_record_key,
                issue_status,
                severity,
                issue_summary,
                issue_details,
                assigned_steward,
                opened_at,
                resolved_at,
                resolution_notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                f"ISSUE{idx:06d}",
                dq_rule_id,
                source_table,
                str(random.randint(1, 5000)),
                status,
                severity,
                f"Potential data quality issue on {source_table}.{source_column or 'record'}",
                fake.sentence(nb_words=14),
                fake.name(),
                opened_at,
                resolved_at,
                "Resolved during sample stewardship review." if resolved_at else None,
            ),
        )

    return print_count(cur, "stewardship_issues")


def load_source_to_target_mappings(cur):
    mapping_candidates = [
        ("customers", "customer_id", "RAW", "raw_customers", "customer_id"),
        ("customers", "customer_number", "CURATED", "dim_customer", "customer_number"),
        ("customers", "first_name", "CURATED", "dim_customer", "first_name"),
        ("customers", "last_name", "CURATED", "dim_customer", "last_name"),
        ("customers", "email", "CURATED", "dim_customer", "email_address"),
        ("customers", "customer_status", "CURATED", "dim_customer", "customer_status"),
        ("accounts", "account_id", "RAW", "raw_accounts", "account_id"),
        ("accounts", "account_number", "CURATED", "dim_account", "account_number"),
        ("accounts", "customer_id", "CURATED", "dim_account", "customer_id"),
        ("accounts", "product_id", "CURATED", "dim_account", "product_id"),
        ("accounts", "current_balance", "CURATED", "fact_account_balance", "current_balance"),
        ("accounts", "account_status", "CURATED", "dim_account", "account_status"),
        ("transactions", "transaction_id", "RAW", "raw_transactions", "transaction_id"),
        ("transactions", "transaction_reference", "CURATED", "fact_transaction", "transaction_reference"),
        ("transactions", "account_id", "CURATED", "fact_transaction", "account_id"),
        ("transactions", "transaction_type", "CURATED", "fact_transaction", "transaction_type"),
        ("transactions", "amount", "CURATED", "fact_transaction", "transaction_amount"),
        ("transactions", "transaction_status", "CURATED", "fact_transaction", "transaction_status"),
        ("branches", "branch_code", "CURATED", "dim_branch", "branch_code"),
        ("branches", "branch_name", "CURATED", "dim_branch", "branch_name"),
        ("products", "product_code", "CURATED", "dim_product", "product_code"),
        ("products", "product_type", "CURATED", "dim_product", "product_type"),
        ("customer_risk_scores", "risk_score", "CURATED", "fact_customer_risk", "risk_score"),
        ("customer_risk_scores", "risk_band", "CURATED", "fact_customer_risk", "risk_band"),
        ("data_quality_rules", "rule_code", "GOVERNANCE", "dq_rule_catalog", "rule_code"),
    ]

    for idx, (source_table, source_column, target_layer, target_table, target_column) in enumerate(
        mapping_candidates[:NUM_MAPPINGS],
        start=1,
    ):
        cur.execute(
            """
            INSERT INTO source_to_target_mappings (
                mapping_name,
                source_table,
                source_column,
                target_layer,
                target_table,
                target_column,
                transformation_rule,
                business_definition,
                data_owner,
                data_steward
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                f"MAP{idx:03d}_{source_table}_{source_column}",
                source_table,
                source_column,
                target_layer,
                target_table,
                target_column,
                "Direct mapping; data type normalization may apply in later pipeline layers.",
                f"Maps source field {source_table}.{source_column} to {target_layer}.{target_table}.{target_column}.",
                random.choice(["Retail Banking", "Risk Management", "Data Governance"]),
                random.choice(["Customer Data Steward", "Account Data Steward", "Risk Data Steward"]),
            ),
        )

    return print_count(cur, "source_to_target_mappings")


def main():
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
        )
        conn.autocommit = False
        cur = conn.cursor()

        clear_existing_data(cur)
        load_reference_codes(cur)
        branches = load_branches(cur)
        products = load_products(cur)
        customers = load_customers(cur, branches)
        accounts = load_accounts(cur, customers, products, branches)
        load_transactions(cur, accounts, branches)
        load_customer_risk_scores(cur, customers)
        dq_rules = load_data_quality_rules(cur)
        load_stewardship_issues(cur, dq_rules)
        load_source_to_target_mappings(cur)

        conn.commit()
        print("Synthetic banking source data load completed.")

    except Exception as exc:
        if conn:
            conn.rollback()
        print(f"Data load failed and was rolled back: {exc}", file=sys.stderr)
        sys.exit(1)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    main()
