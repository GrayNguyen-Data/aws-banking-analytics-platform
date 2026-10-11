"""
Script tiện ích: Xem toàn bộ CloudWatch Logs của Banking DWH Pipeline
=====================================================================
Tự động quét và hiển thị log mới nhất từ cả 4 hàm Lambda trong ap-southeast-1:
1. clean_load_staging
2. build_warehouse
3. build_marts
4. alert_on_failure
"""

import sys
import boto3
from datetime import datetime

# Thiết lập mã hóa UTF-8 cho console
sys.stdout.reconfigure(encoding="utf-8")

LAMBDA_FUNCTIONS = [
    ("clean_load_staging", "📥 GIAI ĐOẠN 1: CLEAN & LOAD STAGING"),
    ("build_warehouse", "🏗️ GIAI ĐOẠN 2: BUILD WAREHOUSE (STAR SCHEMA)"),
    ("build_marts", "📊 GIAI ĐOẠN 3: BUILD DATA MARTS"),
    ("alert_on_failure", "🔔 GIAI ĐOẠN 4: PIPELINE ALERTS & NOTIFICATIONS")
]

def print_banner():
    print("=" * 80)
    print("      APEX BANK DATA PLATFORM — CLOUDWATCH LOGS MONITORING")
    print(f"      Thời gian kiểm tra: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

def fetch_latest_logs(logs_client, function_name, title):
    log_group_name = f"/aws/lambda/{function_name}"
    print(f"\n{title}")
    print(f"Log Group: {log_group_name}")
    print("-" * 80)

    try:
        streams = logs_client.describe_log_streams(
            logGroupName=log_group_name,
            orderBy="LastEventTime",
            descending=True,
            limit=1
        )
        log_streams = streams.get("logStreams", [])
        if not log_streams:
            print("  (Chưa có log stream nào được tạo)")
            return

        latest_stream = log_streams[0]["logStreamName"]
        last_event_time = datetime.fromtimestamp(log_streams[0]["lastEventTimestamp"] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
        print(f"Stream mới nhất: {latest_stream}")
        print(f"Thời gian sự kiện: {last_event_time}")
        print("-" * 80)

        events_response = logs_client.get_log_events(
            logGroupName=log_group_name,
            logStreamName=latest_stream,
            limit=40
        )
        
        events = events_response.get("events", [])
        if not events:
            print("  (Stream rỗng)")
            return

        for event in events:
            msg = event["message"].rstrip()
            # Bỏ qua các dòng init hệ thống ngắn để dễ nhìn
            if msg.startswith("INIT_START") or msg.startswith("START") or msg.startswith("END"):
                continue
            if msg.startswith("REPORT"):
                print(f"  \033[92m{msg}\033[0m")  # Màu xanh cho REPORT metric
            elif "ERROR" in msg or "Exception" in msg:
                print(f"  \033[91m{msg}\033[0m")  # Màu đỏ cho lỗi
            else:
                print(f"  {msg}")

    except logs_client.exceptions.ResourceNotFoundException:
        print(f"  Log group {log_group_name} chưa tồn tại trên CloudWatch.")
    except Exception as e:
        print(f"  Lỗi khi đọc log: {e}")

def main():
    print_banner()
    logs_client = boto3.client("logs", region_name="ap-southeast-1")
    for fn, title in LAMBDA_FUNCTIONS:
        fetch_latest_logs(logs_client, fn, title)
    print("\n" + "=" * 80)
    print("Hoàn tất quét CloudWatch Logs.")
    print("=" * 80)

if __name__ == "__main__":
    main()
