-- ====================================================================
-- LAB 5: NẠP DỮ LIỆU CÁC BẢNG FACT (KIMBALL CARD & ENTITY LOOKUPS)
-- ====================================================================

-- 1. FACT_TRANSACTIONS (1 triệu dòng)
WITH valid_transactions AS (
    SELECT 
        t.transaction_id,
        t.account_id,
        t.merchant_id,
        t.amount_usd,
        t.transaction_date
    FROM staging.stg_transactions t
    WHERE t.transaction_id IS NOT NULL 
      AND t.account_id IS NOT NULL
      AND t.merchant_id IS NOT NULL
      AND t.amount_usd > 0
      AND t.transaction_date IS NOT NULL
),
unknown_keys AS (
    SELECT 
        (SELECT customer_key FROM warehouse.dim_customer WHERE customer_id = 'UNKNOWN') AS unk_cust_key,
        (SELECT account_key FROM warehouse.dim_account WHERE account_id = 'UNKNOWN') AS unk_acc_key,
        (SELECT card_key FROM warehouse.dim_card WHERE card_id = 'UNKNOWN') AS unk_card_key,
        (SELECT merchant_key FROM warehouse.dim_merchant WHERE merchant_id = 'UNKNOWN') AS unk_merch_key,
        (SELECT branch_key FROM warehouse.dim_branch WHERE branch_id = 'UNKNOWN') AS unk_branch_key
),
enriched_transactions AS (
    SELECT 
        vt.transaction_id,
        COALESCE(c.customer_key, uk.unk_cust_key) AS customer_key,
        COALESCE(a.account_key, uk.unk_acc_key) AS account_key,
        COALESCE(crd.card_key, uk.unk_card_key) AS card_key,
        COALESCE(m.merchant_key, uk.unk_merch_key) AS merchant_key,
        uk.unk_branch_key AS branch_key,
        COALESCE(d.date_key, TO_CHAR(vt.transaction_date, 'YYYYMMDD')::INT) AS date_key,
        vt.amount_usd,
        vt.transaction_date
    FROM valid_transactions vt
    CROSS JOIN unknown_keys uk
    -- 1. Lookup Account & Customer
    LEFT JOIN staging.stg_accounts sa ON vt.account_id = sa.account_id
    LEFT JOIN warehouse.dim_customer c ON sa.customer_id = c.customer_id
    LEFT JOIN warehouse.dim_account a ON vt.account_id = a.account_id
    -- 2. Lookup Card (Ánh xạ thẻ từ account, nếu không có thì gán về External Card)
    LEFT JOIN (
        SELECT DISTINCT ON (account_id) account_id, card_id
        FROM staging.stg_cards
        ORDER BY account_id, expiration_date DESC
    ) sc ON vt.account_id = sc.account_id
    LEFT JOIN warehouse.dim_card crd ON sc.card_id = crd.card_id
    -- 3. Lookup Merchant
    LEFT JOIN warehouse.dim_merchant m ON vt.merchant_id = m.merchant_id
    -- 4. Lookup Date
    LEFT JOIN warehouse.dim_date d ON vt.transaction_date::date = d.full_date
)
INSERT INTO warehouse.fact_transactions (
    transaction_id,
    customer_key,
    account_key,
    card_key,
    merchant_key,
    branch_key,
    date_key,
    amount_usd,
    transaction_date
)
SELECT 
    transaction_id,
    customer_key,
    account_key,
    card_key,
    merchant_key,
    branch_key,
    date_key,
    amount_usd,
    transaction_date
FROM enriched_transactions
ON CONFLICT (transaction_id) DO NOTHING;

-- 2. FACT_LOANS (30,000 dòng)
WITH valid_loans AS (
    SELECT 
        l.loan_id,
        l.customer_id,
        l.loan_amount,
        l.interest_rate,
        l.start_date
    FROM staging.stg_loans l
    WHERE l.loan_id IS NOT NULL 
      AND l.customer_id IS NOT NULL
      AND l.loan_amount > 0
      AND l.interest_rate >= 0
      AND l.start_date IS NOT NULL
),
unknown_keys AS (
    SELECT 
        (SELECT customer_key FROM warehouse.dim_customer WHERE customer_id = 'UNKNOWN') AS unk_cust_key,
        (SELECT branch_key FROM warehouse.dim_branch WHERE branch_id = 'UNKNOWN') AS unk_branch_key
),
enriched_loans AS (
    SELECT 
        vl.loan_id,
        COALESCE(c.customer_key, uk.unk_cust_key) AS customer_key,
        uk.unk_branch_key AS branch_key,
        COALESCE(d.date_key, TO_CHAR(vl.start_date, 'YYYYMMDD')::INT) AS start_date_key,
        vl.loan_amount,
        vl.interest_rate,
        vl.start_date
    FROM valid_loans vl
    CROSS JOIN unknown_keys uk
    LEFT JOIN warehouse.dim_customer c ON vl.customer_id = c.customer_id
    LEFT JOIN warehouse.dim_date d ON vl.start_date = d.full_date
)
INSERT INTO warehouse.fact_loans (
    loan_id,
    customer_key,
    branch_key,
    start_date_key,
    loan_amount,
    interest_rate,
    start_date
)
SELECT 
    loan_id,
    customer_key,
    branch_key,
    start_date_key,
    loan_amount,
    interest_rate,
    start_date
FROM enriched_loans
ON CONFLICT (loan_id) DO NOTHING;