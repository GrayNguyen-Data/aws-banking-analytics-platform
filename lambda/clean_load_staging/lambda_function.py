"""
AWS Lambda Handler: Clean & Load Staging
========================================
Serverless function được kích hoạt bởi EventBridge / S3 / Step Functions để nạp
dữ liệu từ S3 Data Lake vào RDS PostgreSQL Staging schema bằng streaming COPY.
"""

import os
import io
import json
import logging
from datetime import datetime, timezone
import pandas as pd
import psycopg2
import boto3

# Cấu hình Logger để đẩy log lên AWS CloudWatch
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Đọc cấu hình từ AWS Lambda Environment Variables
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-1")
BUCKET_NAME = os.getenv("AWS_S3_BUCKET")
DB_HOST = os.getenv("DB_HOST") or os.getenv("RDS_HOST")
DB_PORT = os.getenv("DB_PORT") or os.getenv("RDS_PORT", "5432")
DB_NAME = os.getenv("DB_NAME") or os.getenv("RDS_DATABASE", "banking_dwh")
DB_USER = os.getenv("DB_USER") or os.getenv("RDS_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD") or os.getenv("RDS_PASSWORD")

# Metadata cấu hình 7 bảng Staging
TABLE_CONFIGS = [
    {
        "table_name": "branches",
        "stg_table": "staging.stg_branches",
        "columns": ["branch_id", "branch_name", "manager_name"],
        "dtype": {"branch_id": str, "branch_name": str, "manager_name": str}
    },
    {
        "table_name": "merchants",
        "stg_table": "staging.stg_merchants",
        "columns": ["merchant_id", "merchant_name", "city"],
        "dtype": {"merchant_id": str, "merchant_name": str, "city": str}
    },
    {
        "table_name": "customers",
        "stg_table": "staging.stg_customers",
        "columns": ["customer_id", "first_name", "last_name", "email", "city", "credit_score", "created_at"],
        "dtype": {"customer_id": str, "first_name": str, "last_name": str, "email": str, "city": str, "credit_score": "Int64"},
        "date_cols": ["created_at"]
    },
    {
        "table_name": "accounts",
        "stg_table": "staging.stg_accounts",
        "columns": ["account_id", "customer_id", "account_type", "balance_usd", "open_date"],
        "dtype": {"account_id": str, "customer_id": str, "account_type": str, "balance_usd": float},
        "date_cols": ["open_date"]
    },
    {
        "table_name": "cards",
        "stg_table": "staging.stg_cards",
        "columns": ["card_id", "account_id", "card_type", "expiration_date"],
        "dtype": {"card_id": str, "account_id": str, "card_type": str},
        "date_cols": ["expiration_date"]
    },
    {
        "table_name": "loans",
        "stg_table": "staging.stg_loans",
        "columns": ["loan_id", "customer_id", "loan_amount", "interest_rate", "start_date"],
        "dtype": {"loan_id": str, "customer_id": str, "loan_amount": float, "interest_rate": float},
        "date_cols": ["start_date"]
    },
    {
        "table_name": "transactions",
        "stg_table": "staging.stg_transactions",
        "columns": ["transaction_id", "account_id", "merchant_id", "amount_usd", "transaction_date"],
        "dtype": {"transaction_id": str, "account_id": str, "merchant_id": str, "amount_usd": float},
        "datetime_cols": ["transaction_date"],
        "chunksize": 250000
    }
]

def get_db_connection():
    """Tạo kết nối tới PostgreSQL RDS qua SSL"""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode="require"
    )

def clean_dataframe(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Làm sạch và chuẩn hóa dữ liệu"""
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].astype(str).str.strip()

    if "date_cols" in config:
        for col in config["date_cols"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")

    if "datetime_cols" in config:
        for col in config["datetime_cols"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")

    return df

def copy_df_to_postgres(cursor, df: pd.DataFrame, table_name: str, columns: list):
    """Nạp nhanh bằng COPY FROM STDIN qua bộ nhớ RAM StringIO"""
    output = io.StringIO()
    df.to_csv(output, sep="\t", header=False, index=False, na_rep="\\N", columns=columns)
    output.seek(0)
    cols_str = ", ".join(columns)
    sql = f"COPY {table_name} ({cols_str}) FROM STDIN WITH (FORMAT CSV, DELIMITER E'\\t', NULL '\\N')"
    cursor.copy_expert(sql, output)

def get_latest_s3_ingest_date(s3_client, bucket_name: str) -> str:
    """Tự động tìm kiếm partition ingest_date mới nhất trên S3"""
    try:
        resp = s3_client.list_objects_v2(Bucket=bucket_name, Prefix="raw/branches/", Delimiter="/")
        prefixes = [p["Prefix"] for p in resp.get("CommonPrefixes", [])]
        dates = []
        for p in prefixes:
            if "ingest_date=" in p:
                d_str = p.split("ingest_date=")[-1].strip("/")
                dates.append(d_str)
        if dates:
            return sorted(dates)[-1]
    except Exception as e:
        logger.warning(f"Không thể quét partition S3 tự động: {e}")
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def lambda_handler(event, context):
    """Entry Point chính của AWS Lambda"""
    s3_client = boto3.client("s3", region_name=AWS_REGION)
    # Lấy ngày từ event hoặc tự động lấy partition mới nhất trên S3
    ingest_date = event.get("ingest_date") or get_latest_s3_ingest_date(s3_client, BUCKET_NAME)
    
    logger.info(f"Bắt đầu Staging ETL Pipeline cho mẻ ngày: {ingest_date}")
    conn = get_db_connection()
    conn.autocommit = False
    cursor = conn.cursor()

    results = {}
    try:
        for config in TABLE_CONFIGS:
            table_name = config["table_name"]
            stg_table = config["stg_table"]
            columns = config["columns"]
            s3_key = f"raw/{table_name}/ingest_date={ingest_date}/{table_name}.csv"

            cursor.execute(f"TRUNCATE TABLE {stg_table};")
            response = s3_client.get_object(Bucket=BUCKET_NAME, Key=s3_key)
            csv_body = response["Body"]

            total_loaded = 0
            if "chunksize" in config:
                for chunk in pd.read_csv(csv_body, dtype=config.get("dtype"), chunksize=config["chunksize"]):
                    chunk = clean_dataframe(chunk, config)
                    copy_df_to_postgres(cursor, chunk, stg_table, columns)
                    total_loaded += len(chunk)
            else:
                df = pd.read_csv(csv_body, dtype=config.get("dtype"))
                df = clean_dataframe(df, config)
                copy_df_to_postgres(cursor, df, stg_table, columns)
                total_loaded = len(df)

            conn.commit()
            results[stg_table] = total_loaded
            logger.info(f"Đã nạp {total_loaded:,} dòng vào {stg_table}")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Staging ETL completed successfully",
                "ingest_date": ingest_date,
                "loaded_rows": results
            })
        }
    except Exception as e:
        conn.rollback()
        logger.error(f"Lỗi Staging ETL: {e}", exc_info=True)
        raise e
    finally:
        cursor.close()
        conn.close()
