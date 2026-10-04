"""
DATA PROFILING & EXPLORATORY DATA ANALYSIS (EDA)
================================================
Đọc mẫu từ S3 Data Lake để kiểm tra danh sách cột, kiểu dữ liệu và vài dòng mẫu
của toàn bộ 7 bảng nhằm phục vụ thiết kế Star Schema.
"""

import os
import io
from datetime import datetime, timezone
import pandas as pd
import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-1")
BUCKET_NAME = os.getenv("AWS_S3_BUCKET")
INGEST_DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d")

TABLES = ["customers", "accounts", "cards", "merchants", "branches", "loans", "transactions"]

def run_profiling():
    s3_client = boto3.client("s3", region_name=AWS_REGION)
    
    print("=" * 80)
    print(f"📊 BÁO CÁO PHÂN TÍCH SCHEMA CỦA 7 BẢNG TỪ S3 (Mẻ: {INGEST_DATE})")
    print("=" * 80)

    for table in TABLES:
        s3_key = f"raw/{table}/ingest_date={INGEST_DATE}/{table}.csv"
        try:
            # Đọc 10 dòng đầu để xem cấu trúc và kiểu dữ liệu
            response = s3_client.get_object(Bucket=BUCKET_NAME, Key=s3_key)
            df = pd.read_csv(io.BytesIO(response['Body'].read()), nrows=10)
            
            print(f"\n📂 BẢNG: [{table.upper()}] (Đường dẫn: s3://{BUCKET_NAME}/{s3_key})")
            print(f"  - Số lượng cột: {len(df.columns)}")
            print(f"  - Danh sách cột: {list(df.columns)}")
            print("\n  --- Dữ liệu mẫu (2 dòng đầu) ---")
            print(df.head(2).to_string(index=False))
            print("-" * 80)
            
        except Exception as e:
            print(f"❌ Lỗi khi đọc bảng {table}: {e}")

if __name__ == "__main__":
    run_profiling()
