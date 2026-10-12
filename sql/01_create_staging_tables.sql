-- 1. Staging Customers
CREATE TABLE IF NOT EXISTS staging.stg_customers (
    customer_id VARCHAR(50),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(150),
    city VARCHAR(100),
    credit_score INT,
    created_at DATE,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Staging Accounts
CREATE TABLE IF NOT EXISTS staging.stg_accounts (
    account_id VARCHAR(50),
    customer_id VARCHAR(50),
    account_type VARCHAR(50),
    balance_usd NUMERIC(15, 2),
    open_date DATE,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Staging Cards
CREATE TABLE IF NOT EXISTS staging.stg_cards (
    card_id VARCHAR(50),
    account_id VARCHAR(50),
    card_type VARCHAR(50),
    expiration_date DATE,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Staging Merchants
CREATE TABLE IF NOT EXISTS staging.stg_merchants (
    merchant_id VARCHAR(50),
    merchant_name VARCHAR(150),
    city VARCHAR(100),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Staging Branches
CREATE TABLE IF NOT EXISTS staging.stg_branches (
    branch_id VARCHAR(50),
    branch_name VARCHAR(150),
    manager_name VARCHAR(100),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Staging Loans
CREATE TABLE IF NOT EXISTS staging.stg_loans (
    loan_id VARCHAR(50),
    customer_id VARCHAR(50),
    loan_amount NUMERIC(15, 2),
    interest_rate NUMERIC(6, 2),
    start_date DATE,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Staging Transactions (1 triệu bản ghi)
CREATE TABLE IF NOT EXISTS staging.stg_transactions (
    transaction_id VARCHAR(100),
    account_id VARCHAR(50),
    merchant_id VARCHAR(50),
    amount_usd NUMERIC(15, 2),
    transaction_date TIMESTAMP,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
