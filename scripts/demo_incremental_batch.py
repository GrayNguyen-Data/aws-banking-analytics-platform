"""
================================================================================
🏦 APEX BANK — LIVE DEMO & INCREMENTAL BATCH SIMULATOR
================================================================================
Kịch bản Demo chuyên nghiệp cho Doanh nghiệp / Tuyển dụng:
1. Bơm mẻ giao dịch mới (Incremental Batch - 5,000 transactions) ngày 2026-10-12
2. Tự động tính toán & cập nhật lại toàn bộ 4 Data Marts (mart.*)
3. So sánh trực quan TRƯỚC vs SAU trên Terminal
4. Hướng dẫn mở Streamlit Dashboard để mục sở thị số liệu & biểu đồ nhảy trực tiếp
================================================================================
"""

import os
import sys
import time
from datetime import datetime
import psycopg2
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()

DB_HOST = os.getenv("DB_HOST") or os.getenv("RDS_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "banking_dwh")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode="require"
    )

def get_current_metrics(conn):
    """Lấy số liệu hiện tại của DWH"""
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), COALESCE(SUM(amount_usd), 0) FROM warehouse.fact_transactions;")
    row_txn = cur.fetchone()
    
    cur.execute("SELECT COUNT(*) FROM warehouse.fact_transactions WHERE transaction_id LIKE 'TXN_DEMO_%';")
    demo_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM mart.customer_360;")
    c360_cnt = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM mart.daily_branch_performance;")
    branch_cnt = cur.fetchone()[0]

    cur.close()
    return {
        "total_txns": row_txn[0],
        "total_volume": float(row_txn[1]),
        "demo_txns": demo_count,
        "customer_360_rows": c360_cnt,
        "branch_rows": branch_cnt
    }

def inject_incremental_batch(num_records=5000):
    """Sinh và nạp mẻ giao dịch mới phát sinh hôm nay"""
    print("\n" + "=" * 80)
    print(f"🚀 BẮT ĐẦU BƠM MẺ DỮ LIỆU GIAO DỊCH MỚI ({num_records:,} TRANSACTIONS)...")
    print("=" * 80)

    conn = get_connection()
    before = get_current_metrics(conn)

    print(f"📊 Số liệu hiện tại:")
    print(f"   • Tổng số giao dịch : {before['total_txns']:,} transactions")
    print(f"   • Tổng giá trị       : ${before['total_volume']:,.2f} USD")
    print(f"   • Giao dịch demo cũ  : {before['demo_txns']:,} records")

    cur = conn.cursor()
    
    # Đảm bảo dim_date có ngày hôm nay 2026-10-12
    cur.execute("""
    INSERT INTO warehouse.dim_date (date_key, full_date, day_of_week, day_name, month, month_name, quarter, year, is_weekend)
    VALUES (20261012, '2026-10-12', 1, 'Monday', 10, 'October', 4, 2026, FALSE)
    ON CONFLICT (date_key) DO NOTHING;
    """)

    print("\n⏳ Đang sinh 5,000 giao dịch mới gắn với khách hàng, thẻ và chi nhánh có thực...")

    sql_inject = f"""
    WITH sample_customers AS (
        SELECT customer_key FROM warehouse.dim_customer WHERE customer_id != 'UNKNOWN' LIMIT 2000
    ),
    sample_accounts AS (
        SELECT account_key FROM warehouse.dim_account WHERE account_id != 'UNKNOWN' LIMIT 2000
    ),
    sample_cards AS (
        SELECT card_key FROM warehouse.dim_card WHERE card_id != 'UNKNOWN' LIMIT 1000
    ),
    sample_merchants AS (
        SELECT merchant_key FROM warehouse.dim_merchant WHERE merchant_id != 'UNKNOWN' LIMIT 500
    ),
    sample_branches AS (
        SELECT branch_key FROM warehouse.dim_branch WHERE branch_id != 'UNKNOWN' LIMIT 100
    )
    INSERT INTO warehouse.fact_transactions (
        transaction_id, customer_key, account_key, card_key, merchant_key, branch_key,
        date_key, amount_usd, transaction_date
    )
    SELECT 
        'TXN_DEMO_' || LPAD(s.i::text, 6, '0') AS transaction_id,
        (SELECT customer_key FROM sample_customers OFFSET (s.i % 1990) LIMIT 1) AS customer_key,
        (SELECT account_key FROM sample_accounts OFFSET (s.i % 1990) LIMIT 1) AS account_key,
        (SELECT card_key FROM sample_cards OFFSET (s.i % 990) LIMIT 1) AS card_key,
        (SELECT merchant_key FROM sample_merchants OFFSET (s.i % 490) LIMIT 1) AS merchant_key,
        (SELECT branch_key FROM sample_branches OFFSET (s.i % 95) LIMIT 1) AS branch_key,
        20261012 AS date_key,
        -- Sinh số tiền giao dịch từ $500 đến $75,000 (mẻ giao dịch lớn làm nổi bật biểu đồ)
        ROUND((500 + (s.i * 14.5) % 74500)::numeric, 2) AS amount_usd,
        '2026-10-12 10:30:00'::timestamp + (s.i || ' seconds')::interval AS transaction_date
    FROM generate_series(1, {num_records}) AS s(i)
    ON CONFLICT (transaction_id) DO NOTHING;
    """

    start_time = time.time()
    cur.execute(sql_inject)
    conn.commit()
    insert_duration = time.time() - start_time
    print(f"✅ Đã nạp thành công {num_records:,} transactions vào `warehouse.fact_transactions` ({insert_duration:.2f}s)!")

    # Cập nhật lại 4 Data Marts
    print("\n⏳ Đang tự động làm mới (Refresh) toàn bộ 4 Data Marts `mart.*`...")
    with open("sql/06_create_data_marts.sql", "r", encoding="utf-8") as f:
        marts_sql = f.read()

    start_marts = time.time()
    cur.execute(marts_sql)
    conn.commit()
    marts_duration = time.time() - start_marts
    print(f"🎉 Hoàn tất tính toán Data Marts trong {marts_duration:.2f}s!")

    after = get_current_metrics(conn)
    cur.close()
    conn.close()

    print("\n" + "=" * 80)
    print("📈 BẢNG SO SÁNH TRƯỚC VÀ SAU KHI NẠP MẺ INCREMENTAL DATA")
    print("=" * 80)
    diff_txns = after["total_txns"] - before["total_txns"]
    diff_vol = after["total_volume"] - before["total_volume"]
    print(f" Chỉ số (Metric)        | TRƯỚC KHI NẠP           | SAU KHI NẠP (HIỆN TẠI)  | THAY ĐỔI")
    print(f"------------------------+-------------------------+-------------------------+-------------------")
    print(f" Total Transactions     | {before['total_txns']:>19,} rows | {after['total_txns']:>19,} rows | 🟢 +{diff_txns:,}")
    print(f" Total Volume (USD)     | ${before['total_volume']:>18,.2f} | ${after['total_volume']:>18,.2f} | 🟢 +${diff_vol:,.2f}")
    print(f" Branch Performance Rows| {before['branch_rows']:>19,} rows | {after['branch_rows']:>19,} rows | 🟢 +{after['branch_rows'] - before['branch_rows']:,}")
    print("=" * 80)
    print("\n💡 HƯỚNG DẪN XEM KẾT QUẢ TRỰC QUAN:")
    print("1. Chạy lệnh: `streamlit run dashboard/app.py`")
    print("2. Trên thanh Sidebar, bấm nút '🔄 Làm mới dữ liệu (Clear Cache)'")
    print("3. Bác sẽ thấy các thẻ KPI và biểu đồ giao dịch nhảy số tăng lên ngay trước mắt!")
    print("=" * 80 + "\n")

def reset_demo_data():
    """Xóa các giao dịch demo và hoàn nguyên dữ liệu chuẩn"""
    print("\n" + "=" * 80)
    print("🧹 BẮT ĐẦU HOÀN NGUYÊN (RESET) DỮ LIỆU DEMO VỀ TRẠNG THÁI GỐC...")
    print("=" * 80)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM warehouse.fact_transactions WHERE transaction_id LIKE 'TXN_DEMO_%';")
    conn.commit()
    print("✅ Đã xóa toàn bộ giao dịch Demo khỏi `warehouse.fact_transactions`!")

    print("⏳ Đang tính toán lại Data Marts...")
    # Chạy lại rebuild marts chuẩn
    with open("sql/06_create_data_marts.sql", "r", encoding="utf-8") as f:
        sql = f.read()
    cur.execute(sql)
    conn.commit()
    print("🎉 Hoàn tất hoàn nguyên Data Marts về trạng thái ban đầu!")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--reset":
            reset_demo_data()
            sys.exit(0)
        elif sys.argv[1] == "--inject":
            num = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
            inject_incremental_batch(num)
            sys.exit(0)

    print("\nCHỌN HÀNH ĐỘNG DEMO:")
    print("  1. Bơm mẻ 5,000 giao dịch mới (Demo Live Incremental Ingestion)")
    print("  2. Reset dữ liệu về ban đầu (Xóa mẻ demo)")
    print("  3. Thoát")
    try:
        choice = input("\nNhập lựa chọn của bác (1/2/3) [Mặc định: 1]: ").strip()
    except EOFError:
        choice = "1"

    if choice == "2":
        reset_demo_data()
    elif choice == "3":
        print("Đã thoát.")
    else:
        inject_incremental_batch(5000)
