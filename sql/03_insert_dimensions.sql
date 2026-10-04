-- ====================================================================
-- LAB 5: NẠP DỮ LIỆU CÁC BẢNG DIMENSION (KIMBALL MASTER DATA + EXTERNAL GUEST MEMBERS)
-- ====================================================================

-- ------------------------------------------------------------
-- BƯỚC 1: CHÈN BẢN GHI MẶC ĐỊNH "EXTERNAL / GUEST MEMBER"
-- (Đại diện cho khách hàng vãng lai, thẻ ngoài, đối tác ngoài hệ thống)
-- ------------------------------------------------------------

-- 1.0 External / Guest Customer
INSERT INTO warehouse.dim_customer (
    customer_id, first_name, last_name, full_name, email, city, credit_score, created_at
) VALUES (
    'UNKNOWN', 'External', 'Customer', 'External / Guest Customer', 'external-guest@bank.internal', 'Unknown City', -1, '1900-01-01'
) ON CONFLICT (customer_id) DO NOTHING;

-- 2.0 External Account
INSERT INTO warehouse.dim_account (
    account_id, account_type, balance_usd, open_date
) VALUES (
    'UNKNOWN', 'EXTERNAL_ACCOUNT', 0.00, '1900-01-01'
) ON CONFLICT (account_id) DO NOTHING;

-- 3.0 External Card (Thẻ ngân hàng ngoài / quốc tế)
INSERT INTO warehouse.dim_card (
    card_id, card_type, expiration_date
) VALUES (
    'UNKNOWN', 'EXTERNAL_CARD', '1900-01-01'
) ON CONFLICT (card_id) DO NOTHING;

-- 4.0 External Merchant (Đối tác ngoài mạng lưới)
INSERT INTO warehouse.dim_merchant (
    merchant_id, merchant_name, city
) VALUES (
    'UNKNOWN', 'Unregistered / External Merchant', 'Unknown City'
) ON CONFLICT (merchant_id) DO NOTHING;

-- 5.0 General Branch (Giao dịch Online / Cổng điện tử)
INSERT INTO warehouse.dim_branch (
    branch_id, branch_name, manager_name
) VALUES (
    'UNKNOWN', 'General / Online Branch', 'Unassigned'
) ON CONFLICT (branch_id) DO NOTHING;


-- ------------------------------------------------------------
-- BƯỚC 2: NẠP MASTER DATA TỪ TẦNG STAGING VÀO DIMENSION (CÓ LÀM SẠCH)
-- ------------------------------------------------------------

-- 1. DIM_CUSTOMER (50,000 bản ghi gốc)
WITH validated_customers AS (
    SELECT 
        TRIM(customer_id) AS customer_id,
        INITCAP(NULLIF(TRIM(first_name), '')) AS first_name,
        INITCAP(NULLIF(TRIM(last_name), '')) AS last_name,
        CASE 
            WHEN LOWER(TRIM(email)) ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' 
            THEN LOWER(TRIM(email))
            ELSE 'invalid-email@bank.internal'
        END AS email,
        INITCAP(NULLIF(TRIM(city), '')) AS city,
        CASE 
            WHEN credit_score BETWEEN 300 AND 850 THEN credit_score
            ELSE -1
        END AS credit_score,
        COALESCE(created_at, CURRENT_DATE) AS created_at
    FROM staging.stg_customers
    WHERE customer_id IS NOT NULL AND TRIM(customer_id) != ''
)
INSERT INTO warehouse.dim_customer (
    customer_id, first_name, last_name, full_name, email, city, credit_score, created_at
)
SELECT 
    customer_id,
    COALESCE(first_name, 'Unknown') AS first_name,
    COALESCE(last_name, 'Customer') AS last_name,
    CONCAT(COALESCE(first_name, 'Unknown'), ' ', COALESCE(last_name, 'Customer')) AS full_name,
    email,
    COALESCE(city, 'Unknown City') AS city,
    credit_score,
    created_at
FROM validated_customers
ON CONFLICT (customer_id) DO UPDATE SET
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    full_name = EXCLUDED.full_name,
    email = EXCLUDED.email,
    city = EXCLUDED.city,
    credit_score = EXCLUDED.credit_score;

-- 2. DIM_ACCOUNT (75,000 bản ghi gốc)
WITH validated_accounts AS (
    SELECT 
        TRIM(account_id) AS account_id,
        CASE 
            WHEN UPPER(TRIM(account_type)) IN ('CHECKING', 'SAVINGS', 'INVESTMENT', 'CREDIT') 
            THEN UPPER(TRIM(account_type))
            ELSE 'OTHER'
        END AS account_type,
        COALESCE(balance_usd, 0.00) AS balance_usd,
        COALESCE(open_date, CURRENT_DATE) AS open_date
    FROM staging.stg_accounts
    WHERE account_id IS NOT NULL AND TRIM(account_id) != ''
)
INSERT INTO warehouse.dim_account (
    account_id, account_type, balance_usd, open_date
)
SELECT 
    account_id,
    account_type,
    balance_usd,
    open_date
FROM validated_accounts
ON CONFLICT (account_id) DO UPDATE SET
    account_type = EXCLUDED.account_type,
    balance_usd = EXCLUDED.balance_usd,
    open_date = EXCLUDED.open_date;

-- 3. DIM_CARD (100,000 bản ghi gốc)
WITH validated_cards AS (
    SELECT 
        TRIM(card_id) AS card_id,
        CASE 
            WHEN UPPER(TRIM(card_type)) IN ('DEBIT', 'CREDIT', 'PREPAID') 
            THEN UPPER(TRIM(card_type))
            ELSE 'STANDARD'
        END AS card_type,
        expiration_date
    FROM staging.stg_cards
    WHERE card_id IS NOT NULL AND TRIM(card_id) != ''
)
INSERT INTO warehouse.dim_card (
    card_id, card_type, expiration_date
)
SELECT 
    card_id,
    card_type,
    expiration_date
FROM validated_cards
ON CONFLICT (card_id) DO UPDATE SET
    card_type = EXCLUDED.card_type,
    expiration_date = EXCLUDED.expiration_date;

-- 4. DIM_MERCHANT (5,000 bản ghi gốc)
WITH validated_merchants AS (
    SELECT 
        TRIM(merchant_id) AS merchant_id,
        COALESCE(NULLIF(TRIM(merchant_name), ''), 'Unknown Merchant') AS merchant_name,
        COALESCE(INITCAP(NULLIF(TRIM(city), '')), 'Unknown City') AS city
    FROM staging.stg_merchants
    WHERE merchant_id IS NOT NULL AND TRIM(merchant_id) != ''
)
INSERT INTO warehouse.dim_merchant (
    merchant_id, merchant_name, city
)
SELECT 
    merchant_id,
    merchant_name,
    city
FROM validated_merchants
ON CONFLICT (merchant_id) DO UPDATE SET
    merchant_name = EXCLUDED.merchant_name,
    city = EXCLUDED.city;

-- 5. DIM_BRANCH (500 bản ghi gốc)
WITH validated_branches AS (
    SELECT 
        TRIM(branch_id) AS branch_id,
        COALESCE(NULLIF(TRIM(branch_name), ''), 'General Branch') AS branch_name,
        COALESCE(INITCAP(NULLIF(TRIM(manager_name), '')), 'Unassigned') AS manager_name
    FROM staging.stg_branches
    WHERE branch_id IS NOT NULL AND TRIM(branch_id) != ''
)
INSERT INTO warehouse.dim_branch (
    branch_id, branch_name, manager_name
)
SELECT 
    branch_id,
    branch_name,
    manager_name
FROM validated_branches
ON CONFLICT (branch_id) DO UPDATE SET
    branch_name = EXCLUDED.branch_name,
    manager_name = EXCLUDED.manager_name;
