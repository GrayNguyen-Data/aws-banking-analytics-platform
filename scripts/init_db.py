"""
DATABASE INITIALIZATION SCRIPT (RDS POSTGRESQL)
================================================
Thực thi các file DDL SQL để tạo Schemas, Bảng Staging, Bảng Warehouse (Star Schema)
và đánh Index tối ưu hóa truy vấn.
"""

import os
from datetime import datetime, timedelta
import psycopg2
from dotenv import load_dotenv

# 1. Tải cấu hình từ .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

SQL_FILES = [
    "sql/00_create_schemas.sql",
    "sql/01_create_staging_tables.sql",
    "sql/02_create_warehouse_tables.sql",
    "sql/05_create_indexes.sql"
]

def populate_dim_date(conn):
    """
    Tự động sinh dữ liệu lịch (Calendar Dates) từ năm 2018 đến 2030
    vào bảng warehouse.dim_date để phục vụ phân tích nghiệp vụ.
    """
    print("\n📅 Đang tự động khởi tạo dữ liệu cho bảng warehouse.dim_date (2018 - 2030)...")
    cursor = conn.cursor()
    
    start_date = datetime(2018, 1, 1)
    end_date = datetime(2030, 12, 31)
    current_date = start_date

    insert_sql = """
    INSERT INTO warehouse.dim_date (
        date_key, full_date, day_of_week, day_name, day_of_month,
        month, month_name, quarter, year, is_weekend
    ) VALUES %s
        ON CONFLICT (date_key) DO NOTHING;
    """

    records = []
    while current_date <= end_date:
        date_key = int(current_date.strftime("%Y%m%d"))
        full_date = current_date.date()
        day_of_week = current_date.weekday() + 1  # 1: Monday, 7: Sunday
        day_name = current_date.strftime("%A")
        day_of_month = current_date.day
        month = current_date.month
        month_name = current_date.strftime("%B")
        quarter = (month - 1) // 3 + 1
        year = current_date.year
        is_weekend = day_of_week in [6, 7]

        records.append((
            date_key, full_date, day_of_week, day_name, day_of_month,
            month, month_name, quarter, year, is_weekend
        ))
        current_date += timedelta(days=1)

    from psycopg2.extras import execute_values
    execute_values(cursor, insert_sql, records, page_size=1000)
    conn.commit()
    cursor.close()
    print(f"✅ Đã nạp thành công {len(records):,} ngày vào warehouse.dim_date!")

def init_database():
    print("=" * 70)
    print("🚀 BẮT ĐẦU KHỞI TẠO CƠ SỞ DỮ LIỆU DATA WAREHOUSE TRÊN POSTGRESQL")
    print(f"- Máy chủ (Host) : {DB_HOST}")
    print(f"- Cổng (Port)    : {DB_PORT}")
    print(f"- Database       : {DB_NAME}")
    print(f"- User           : {DB_USER}")
    print("=" * 70)

    try:
        # Kết nối tới PostgreSQL
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=10
        )
        conn.autocommit = True
        cursor = conn.cursor()
        print("✅ Kết nối tới PostgreSQL thành công!\n")

        # Lần lượt thực thi từng file SQL
        for sql_file in SQL_FILES:
            if not os.path.exists(sql_file):
                print(f"⚠️ Cảnh báo: Không tìm thấy file {sql_file}")
                continue

            print(f"⚙️ Đang thực thi: {sql_file}...")
            with open(sql_file, "r", encoding="utf-8") as f:
                sql_script = f.read().strip()
                if sql_script:
                    cursor.execute(sql_script)
                    print(f"  -> Hoàn thành {sql_file}")
                else:
                    print(f"  -> File {sql_file} rỗng, bỏ qua.")

        cursor.close()

        # Nạp dữ liệu mặc định cho Dim Date
        populate_dim_date(conn)

        conn.close()
        print("\n" + "=" * 70)
        print("🎉 KHỞI TẠO CƠ SỞ DỮ LIỆU HOÀN TOÀN THÀNH CÔNG RỰC RỠ!")
        print("- Đã tạo các Schema: staging, warehouse, mart")
        print("- Đã tạo 7 bảng Staging")
        print("- Đã tạo 6 bảng Dim & 2 bảng Fact (Star Schema)")
        print("- Đã đánh Index tối ưu truy vấn")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ LỖI KHỞI TẠO DATABASE: {e}")
        print("Gợi ý khắc phục:")
        print("1. Kiểm tra xem máy chủ RDS PostgreSQL đã bật (Available) chưa.")
        print("2. Kiểm tra Security Group trên AWS RDS đã mở Inbound Rule Port 5432 chưa.")

if __name__ == "__main__":
    init_database()
