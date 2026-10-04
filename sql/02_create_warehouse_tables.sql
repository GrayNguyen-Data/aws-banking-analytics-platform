-- Xóa bảng cũ để làm mới cấu trúc Star Schema chuẩn
DROP SCHEMA IF EXISTS warehouse CASCADE;

CREATE SCHEMA warehouse;

-- ============================================================
-- 1. DIMENSION TABLES (CÁC BẢNG CHIỀU BAO QUANH)
-- ============================================================

-- 1. Dim Date
CREATE TABLE warehouse.dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL,
    day_of_week INT,
    day_name VARCHAR(20),
    day_of_month INT,
    month INT,
    month_name VARCHAR(20),
    quarter INT,
    year INT,
    is_weekend BOOLEAN
);

-- 2. Dim Customer
CREATE TABLE warehouse.dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(200),
    email VARCHAR(150),
    city VARCHAR(100),
    credit_score INT,
    created_at DATE
);

-- 3. Dim Account
CREATE TABLE warehouse.dim_account (
    account_key SERIAL PRIMARY KEY,
    account_id VARCHAR(50) UNIQUE NOT NULL,
    account_type VARCHAR(50),
    balance_usd NUMERIC(15, 2),
    open_date DATE
);

-- 4. Dim Merchant
CREATE TABLE warehouse.dim_merchant (
    merchant_key SERIAL PRIMARY KEY,
    merchant_id VARCHAR(50) UNIQUE NOT NULL,
    merchant_name VARCHAR(150),
    city VARCHAR(100)
);

-- 5. Dim Branch (Chi nhánh)
CREATE TABLE warehouse.dim_branch (
    branch_key SERIAL PRIMARY KEY,
    branch_id VARCHAR(50) UNIQUE NOT NULL,
    branch_name VARCHAR(150),
    manager_name VARCHAR(100)
);

-- 6. Dim Card (Thẻ ngân hàng)
CREATE TABLE warehouse.dim_card (
    card_key SERIAL PRIMARY KEY,
    card_id VARCHAR(50) UNIQUE NOT NULL,
    card_type VARCHAR(50),
    expiration_date DATE
);

-- ============================================================
-- 2. FACT TABLES (TRUNG TÂM KẾT NỐI TẤT CẢ CÁC BẢNG DIM)
-- ============================================================

-- Fact 1: Fact Transactions (Nối đủ 6 Dim)
CREATE TABLE warehouse.fact_transactions (
    transaction_key BIGSERIAL PRIMARY KEY,
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    customer_key INT REFERENCES warehouse.dim_customer (customer_key),
    account_key INT REFERENCES warehouse.dim_account (account_key),
    card_key INT REFERENCES warehouse.dim_card (card_key),
    merchant_key INT REFERENCES warehouse.dim_merchant (merchant_key),
    branch_key INT REFERENCES warehouse.dim_branch (branch_key),
    date_key INT REFERENCES warehouse.dim_date (date_key),
    amount_usd NUMERIC(15, 2) NOT NULL,
    transaction_date TIMESTAMP NOT NULL,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fact 2: Fact Loans (Nối với Customer, Branch, Date)
CREATE TABLE warehouse.fact_loans (
    loan_key SERIAL PRIMARY KEY,
    loan_id VARCHAR(50) UNIQUE NOT NULL,
    customer_key INT REFERENCES warehouse.dim_customer (customer_key),
    branch_key INT REFERENCES warehouse.dim_branch (branch_key),
    start_date_key INT REFERENCES warehouse.dim_date (date_key),
    loan_amount NUMERIC(15, 2) NOT NULL,
    interest_rate NUMERIC(6, 2) NOT NULL,
    start_date DATE NOT NULL,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);