-- ====================================================================
-- LAB 6: XÂY DỰNG CÁC DATA MARTS CHIẾN LƯỢC (SCHEMA MART)
-- ====================================================================

DROP TABLE IF EXISTS mart.customer_360 CASCADE;

DROP TABLE IF EXISTS mart.daily_branch_performance CASCADE;

DROP TABLE IF EXISTS mart.merchant_analytics CASCADE;

DROP TABLE IF EXISTS mart.credit_risk_monitoring CASCADE;

-- 1. DATA MART: CUSTOMER 360 (CHÂN DUNG KHÁCH HÀNG 360 ĐỘ)
CREATE TABLE mart.customer_360 AS
WITH
    customer_accounts AS (
        SELECT
            sa.customer_id,
            COUNT(a.account_key) AS total_accounts,
            COALESCE(SUM(a.balance_usd), 0.00) AS total_balance_usd
        FROM staging.stg_accounts sa
            JOIN warehouse.dim_account a ON sa.account_id = a.account_id
        GROUP BY
            sa.customer_id
    ),
    customer_spending AS (
        SELECT
            t.customer_key,
            COUNT(t.transaction_key) AS total_transactions,
            COALESCE(SUM(t.amount_usd), 0.00) AS total_spend_usd,
            COALESCE(
                ROUND(AVG(t.amount_usd), 2),
                0.00
            ) AS avg_txn_amount_usd,
            MAX(t.transaction_date) AS last_transaction_date
        FROM warehouse.fact_transactions t
        WHERE
            t.customer_key != (
                SELECT customer_key
                FROM warehouse.dim_customer
                WHERE
                    customer_id = 'UNKNOWN'
            )
        GROUP BY
            t.customer_key
    ),
    customer_loans AS (
        SELECT
            l.customer_key,
            COUNT(l.loan_key) AS active_loans_count,
            COALESCE(SUM(l.loan_amount), 0.00) AS total_loan_debt_usd,
            COALESCE(
                ROUND(AVG(l.interest_rate), 2),
                0.00
            ) AS avg_loan_interest_rate
        FROM warehouse.fact_loans l
        WHERE
            l.customer_key != (
                SELECT customer_key
                FROM warehouse.dim_customer
                WHERE
                    customer_id = 'UNKNOWN'
            )
        GROUP BY
            l.customer_key
    )
SELECT
    c.customer_key,
    c.customer_id,
    c.full_name,
    c.email,
    c.city,
    c.credit_score,
    CASE
        WHEN c.credit_score >= 750 THEN 'EXCELLENT'
        WHEN c.credit_score >= 700 THEN 'GOOD'
        WHEN c.credit_score >= 600 THEN 'FAIR'
        WHEN c.credit_score >= 300 THEN 'POOR'
        ELSE 'UNSCORED'
    END AS credit_tier,
    COALESCE(ca.total_accounts, 0) AS total_accounts,
    COALESCE(ca.total_balance_usd, 0.00) AS total_balance_usd,
    COALESCE(cs.total_transactions, 0) AS total_transactions,
    COALESCE(cs.total_spend_usd, 0.00) AS total_spend_usd,
    COALESCE(cs.avg_txn_amount_usd, 0.00) AS avg_txn_amount_usd,
    cs.last_transaction_date,
    COALESCE(cl.active_loans_count, 0) AS active_loans_count,
    COALESCE(cl.total_loan_debt_usd, 0.00) AS total_loan_debt_usd,
    COALESCE(
        cl.avg_loan_interest_rate,
        0.00
    ) AS avg_loan_interest_rate,
    CASE
        WHEN COALESCE(ca.total_balance_usd, 0) >= 100000
        OR COALESCE(cs.total_spend_usd, 0) >= 50000 THEN 'PLATINUM_VIP'
        WHEN COALESCE(ca.total_balance_usd, 0) >= 30000
        OR COALESCE(cs.total_spend_usd, 0) >= 15000 THEN 'GOLD_AFFLUENT'
        WHEN COALESCE(ca.total_balance_usd, 0) >= 5000 THEN 'SILVER_STANDARD'
        ELSE 'BRONZE_RETAIL'
    END AS customer_segment,
    CURRENT_TIMESTAMP AS mart_updated_at
FROM
    warehouse.dim_customer c
    LEFT JOIN customer_accounts ca ON c.customer_id = ca.customer_id
    LEFT JOIN customer_spending cs ON c.customer_key = cs.customer_key
    LEFT JOIN customer_loans cl ON c.customer_key = cl.customer_key
WHERE
    c.customer_id != 'UNKNOWN';

-- 2. DATA MART: DAILY BRANCH PERFORMANCE
CREATE TABLE mart.daily_branch_performance AS
SELECT
    d.year,
    d.quarter,
    d.month,
    d.month_name,
    d.full_date,
    d.is_weekend,
    b.branch_key,
    b.branch_id,
    b.branch_name,
    b.manager_name,
    COUNT(t.transaction_key) AS daily_transactions_count,
    COALESCE(SUM(t.amount_usd), 0.00) AS daily_transaction_volume_usd,
    COALESCE(
        ROUND(AVG(t.amount_usd), 2),
        0.00
    ) AS avg_ticket_size_usd,
    CURRENT_TIMESTAMP AS mart_updated_at
FROM warehouse.dim_date d
    CROSS JOIN (
        SELECT *
        FROM warehouse.dim_branch
        WHERE
            branch_id != 'UNKNOWN'
        LIMIT 50
    ) b
    LEFT JOIN warehouse.fact_transactions t ON d.date_key = t.date_key
GROUP BY
    d.year,
    d.quarter,
    d.month,
    d.month_name,
    d.full_date,
    d.is_weekend,
    b.branch_key,
    b.branch_id,
    b.branch_name,
    b.manager_name;

-- 3. DATA MART: MERCHANT ANALYTICS
CREATE TABLE mart.merchant_analytics AS
SELECT
    m.merchant_key,
    m.merchant_id,
    m.merchant_name,
    m.city,
    COUNT(t.transaction_key) AS total_transactions,
    COALESCE(SUM(t.amount_usd), 0.00) AS total_sales_volume_usd,
    COALESCE(
        ROUND(AVG(t.amount_usd), 2),
        0.00
    ) AS avg_order_value_usd,
    COALESCE(MIN(t.amount_usd), 0.00) AS min_txn_amount_usd,
    COALESCE(MAX(t.amount_usd), 0.00) AS max_txn_amount_usd,
    ROUND(
        COALESCE(SUM(t.amount_usd), 0.00) * 0.015,
        2
    ) AS estimated_interchange_fee_usd,
    CURRENT_TIMESTAMP AS mart_updated_at
FROM warehouse.dim_merchant m
    LEFT JOIN warehouse.fact_transactions t ON m.merchant_key = t.merchant_key
GROUP BY
    m.merchant_key,
    m.merchant_id,
    m.merchant_name,
    m.city;

-- 4. DATA MART: CREDIT RISK MONITORING
CREATE TABLE mart.credit_risk_monitoring AS
SELECT
    CASE
        WHEN c.credit_score >= 750 THEN '1. EXCELLENT (750 - 850)'
        WHEN c.credit_score >= 700 THEN '2. GOOD (700 - 749)'
        WHEN c.credit_score >= 600 THEN '3. FAIR (600 - 699)'
        WHEN c.credit_score >= 300 THEN '4. POOR (300 - 599)'
        ELSE '5. UNSCORED / GUEST'
    END AS credit_risk_tier,
    COUNT(l.loan_key) AS total_loans_originated,
    COALESCE(SUM(l.loan_amount), 0.00) AS total_loan_debt_usd,
    COALESCE(
        ROUND(AVG(l.loan_amount), 2),
        0.00
    ) AS avg_loan_size_usd,
    COALESCE(
        ROUND(AVG(l.interest_rate), 2),
        0.00
    ) AS avg_interest_rate_pct,
    ROUND(
        SUM(
            l.loan_amount * (l.interest_rate / 100.0)
        ),
        2
    ) AS estimated_annual_interest_revenue_usd,
    CURRENT_TIMESTAMP AS mart_updated_at
FROM warehouse.fact_loans l
    JOIN warehouse.dim_customer c ON l.customer_key = c.customer_key
GROUP BY
    credit_risk_tier;