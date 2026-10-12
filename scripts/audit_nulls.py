import os
import sys
import psycopg2
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST") or os.getenv("RDS_HOST"),
    port=os.getenv("DB_PORT") or "5432",
    dbname=os.getenv("DB_NAME") or "banking_dwh",
    user=os.getenv("DB_USER") or "postgres",
    password=os.getenv("DB_PASSWORD") or os.getenv("RDS_PASSWORD"),
    sslmode="require"
)
cur = conn.cursor()

tables_cols = [
    ("staging.stg_customers", ["customer_id", "first_name", "last_name", "email", "city", "credit_score"]),
    ("staging.stg_accounts", ["account_id", "customer_id", "account_type", "balance_usd", "open_date"]),
    ("staging.stg_cards", ["card_id", "account_id", "card_type", "expiration_date"]),
    ("staging.stg_merchants", ["merchant_id", "merchant_name", "city"]),
    ("staging.stg_branches", ["branch_id", "branch_name", "manager_name"]),
    ("staging.stg_loans", ["loan_id", "customer_id", "loan_amount", "interest_rate", "start_date"]),
    ("staging.stg_transactions", ["transaction_id", "account_id", "merchant_id", "amount_usd", "transaction_date"])
]

print("=" * 75)
print("BÁO CÁO KIỂM TOÁN TỶ LỆ NULL / RỖNG TRONG TẤT CẢ CÁC BẢNG STAGING")
print("=" * 75)

for t, cols in tables_cols:
    cur.execute(f"SELECT COUNT(*) FROM {t};")
    total_rows = cur.fetchone()[0]
    print(f"\n📊 BẢNG: {t.upper()} (Tổng cộng: {total_rows:,} dòng)")
    for c in cols:
        cur.execute(f"SELECT COUNT(*) FROM {t} WHERE {c} IS NULL OR TRIM(CAST({c} AS TEXT)) = '';")
        null_count = cur.fetchone()[0]
        pct = (null_count / total_rows) * 100 if total_rows > 0 else 0
        print(f"   - Cột {c:16}: {null_count:>8,} dòng NULL/Rỗng ({pct:5.2f}%)")

cur.close()
conn.close()
