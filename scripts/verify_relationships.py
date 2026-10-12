import os
import io
from datetime import datetime, timezone
import pandas as pd
import boto3
from dotenv import load_dotenv

import sys
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-1")
BUCKET_NAME = os.getenv("AWS_S3_BUCKET")
INGEST_DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d")

def verify():
    s3 = boto3.client("s3", region_name=AWS_REGION)
    
    def load(table):
        key = f"raw/{table}/ingest_date={INGEST_DATE}/{table}.csv"
        res = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        return pd.read_csv(io.BytesIO(res["Body"].read()))

    print("=" * 70)
    print("KIỂM TRA QUAN HỆ & BẢN CHẤT CARDINALITY TRÊN TẬP DỮ LIỆU THỰC TẾ")
    print("=" * 70)

    customers = load("customers")
    accounts = load("accounts")
    cards = load("cards")
    merchants = load("merchants")
    branches = load("branches")
    loans = load("loans")

    print(f"1. CUSTOMERS: {len(customers):,} dòng, Unique ID: {customers['customer_id'].nunique():,}")
    print(f"2. ACCOUNTS:  {len(accounts):,} dòng, Unique ID: {accounts['account_id'].nunique():,}")
    max_cust_per_acc = accounts.groupby("account_id")["customer_id"].nunique().max()
    print(f"   -> 1 Account có tối đa bao nhiêu Customer? {max_cust_per_acc} (Mỗi Account chỉ thuộc 1 Customer duy nhất -> KHÔNG CÓ nhiều-nhiều N:N)")
    acc_per_cust = accounts.groupby("customer_id")["account_id"].count()
    print(f"   -> 1 Customer có từ {acc_per_cust.min()} đến {acc_per_cust.max()} Account (Trung bình {acc_per_cust.mean():.2f} accounts/customer) -> Quan hệ 1:N chuẩn.")

    print(f"\n3. CARDS:     {len(cards):,} dòng, Unique ID: {cards['card_id'].nunique():,}")
    max_acc_per_crd = cards.groupby("card_id")["account_id"].nunique().max()
    print(f"   -> 1 Card có tối đa bao nhiêu Account? {max_acc_per_crd} (Mỗi thẻ chỉ gắn với 1 Account)")
    crd_per_acc = cards.groupby("account_id")["card_id"].count()
    print(f"   -> 1 Account có từ {crd_per_acc.min()} đến {crd_per_acc.max()} Card (Trung bình {crd_per_acc.mean():.2f} cards/account) -> Quan hệ 1:N.")

    print(f"\n4. LOANS:     {len(loans):,} dòng, Unique ID: {loans['loan_id'].nunique():,}")
    max_cust_per_loan = loans.groupby("loan_id")["customer_id"].nunique().max()
    print(f"   -> 1 Loan có tối đa bao nhiêu Customer? {max_cust_per_loan} (Khoản vay gắn với 1 khách hàng)")
    loans_per_cust = loans.groupby("customer_id")["loan_id"].count()
    print(f"   -> 1 Customer có từ {loans_per_cust.min()} đến {loans_per_cust.max()} Loan (Trung bình {loans_per_cust.mean():.2f} loans/customer) -> Quan hệ 1:N.")

    print(f"\n5. MERCHANTS: {len(merchants):,} dòng, Unique ID: {merchants['merchant_id'].nunique():,}")
    print(f"6. BRANCHES:  {len(branches):,} dòng, Unique ID: {branches['branch_id'].nunique():,}")

    print("\n" + "=" * 70)
    print("KIỂM TRA CỘT TRONG CÁC BẢNG NGUỒN CÓ BRANCH_ID HAY KHÔNG?")
    print("=" * 70)
    for name, df in [("customers", customers), ("accounts", accounts), ("cards", cards), ("loans", loans)]:
        has_branch = "branch_id" in df.columns
        print(f" - Bảng {name:12}: Có branch_id không? {has_branch}")

if __name__ == "__main__":
    verify()
