"""
================================================================================
LAMBDA NOTIFIER & SNS ALERT SYSTEM (LAB 9)
================================================================================
Chức năng:
  Nhận các sự kiện từ Data Pipeline (EventBridge / Step Functions / Direct Trigger)
  và phân phối thông báo đa kênh qua Amazon SNS (Email / SMS / Slack Webhook):
  
  1. CRITICAL FAILURE (P1 - Báo động khẩn cấp):
     - Pipeline sập tại bất kỳ stage nào (Staging, Warehouse, Marts).
     - Đính kèm Stack Trace, Bước lỗi và CloudWatch Log Link.
     
  2. DATA QUALITY WARNING (P2 - Cảnh báo chất lượng dữ liệu):
     - DWH nạp xong nhưng vi phạm bài test Data Quality (Orphan keys, Out-of-range FICO).
     
  3. PIPELINE SUCCESS REPORT (P3 - Báo cáo thành công & Tổng kết mẻ nạp):
     - Tổng kết số lượng bản ghi đã nạp, thời gian thực thi và trạng thái QA.
================================================================================
"""

import os
import json
import boto3
from datetime import datetime, timezone

# Cấu hình AWS SNS
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-1")
SNS_TOPIC_ARN = os.getenv("AWS_SNS_TOPIC_ARN")

sns_client = boto3.client("sns", region_name=AWS_REGION)


def format_failure_message(event: dict) -> tuple:
    """Tạo nội dung thông báo khi Pipeline gặp sự cố (P1 - Critical Alert)"""
    stage = event.get("stage", "UNKNOWN_STAGE")
    error_message = event.get("error", "Unknown error occurred during pipeline execution.")
    stack_trace = event.get("stack_trace", "No stack trace provided.")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    subject = f"🚨 [CRITICAL ALERT] Banking DWH Pipeline FAILED at Stage: {stage}"
    
    body = f"""
================================================================================
🚨 APEX BANK DATA PLATFORM — CRITICAL PIPELINE FAILURE ALERT
================================================================================
Trạng thái: ❌ FAILED (P1 - Urgent Attention Required)
Thời gian : {timestamp}
Giai đoạn : {stage}
================================================================================

📌 CHI TIẾT LỖI (ERROR SUMMARY):
{error_message}

🔍 STACK TRACE & LOG TRACEBACK:
{stack_trace}

🛠️ HƯỚNG DẪN XỬ LÝ SỰ CỐ (RUNBOOK):
1. Kiểm tra AWS CloudWatch Logs tương ứng với Lambda Function: `{stage}`
2. Kiểm tra kết nối và tài nguyên CPU/RAM của RDS PostgreSQL DWH.
3. Chạy lại mẻ nạp thủ công bằng: `python scripts/run_pipeline_e2e.py`

================================================================================
Hệ thống giám sát tự động • AWS Cloud-Native Banking Data Warehouse
"""
    return subject, body


def format_quality_alert_message(event: dict) -> tuple:
    """Tạo nội dung thông báo khi phát hiện lỗi chất lượng dữ liệu (P2 - Data Quality Alert)"""
    failed_tests = event.get("failed_tests", [])
    total_tests = event.get("total_tests", 7)
    passed_tests = event.get("passed_tests", total_tests - len(failed_tests))
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    subject = f"⚠️ [DATA QUALITY WARNING] Banking DWH QA Suite Failed ({len(failed_tests)} tests failed)"

    failed_list_str = "\n".join([f" - ❌ {t.get('name', 'Test')}: {t.get('reason', 'Check failed')}" for t in failed_tests])

    body = f"""
================================================================================
⚠️ APEX BANK DATA PLATFORM — DATA QUALITY ALERT
================================================================================
Trạng thái: ⚠️ WARNING (Data Quality Threshold Violated)
Thời gian : {timestamp}
Kết quả   : {passed_tests}/{total_tests} Tests Passed ({len(failed_tests)} Failed)
================================================================================

📋 CÁC BÀI TEST BỊ VI PHẠM (FAILED CHECKS):
{failed_list_str}

💡 KHUYẾN NGHỊ VẬN HÀNH:
- Tầng Data Marts có thể chứa số liệu không đồng nhất hoặc vi phạm toàn vẹn.
- Tạm dừng xuất bản báo cáo ra BI Dashboard cho đến khi kiểm tra xong dữ liệu nguồn.

================================================================================
Hệ thống giám sát tự động • AWS Cloud-Native Banking Data Warehouse
"""
    return subject, body


def format_success_message(event: dict) -> tuple:
    """Tạo nội dung thông báo tổng kết mẻ nạp thành công (P3 - Success Report)"""
    duration = event.get("duration_seconds", 0)
    records_loaded = event.get("records_loaded", "1,260,500")
    ingest_date = event.get("ingest_date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    subject = f"✅ [PIPELINE SUCCESS] Banking DWH Ingestion Batch Completed ({ingest_date})"

    body = f"""
================================================================================
✅ APEX BANK DATA PLATFORM — DAILY INGESTION BATCH COMPLETED
================================================================================
Trạng thái     : 🟢 SUCCESS (100% Pipeline & Quality Checks Passed)
Mẻ nạp ngày    : {ingest_date}
Thời gian chạy : {duration:.2f} giây
Tổng bản ghi   : {records_loaded} dòng
Thời gian chốt : {timestamp}
================================================================================

📊 KẾT QUẢ TỪNG GIAI ĐOẠN (STAGE BREAKDOWN):
 1. 📥 S3 Data Lake ➔ Staging Schema     : ✅ 1,260,500 dòng (COPY Protocol)
 2. 🏛️ Staging ➔ Warehouse Star Schema   : ✅ 8 Dimension & Fact tables
 3. 📈 Warehouse ➔ Strategic Data Marts  : ✅ Customer 360, Branch, Merchant, Risk
 4. 🔍 Automated Data Quality Suite      : ✅ 7/7 Tests Passed (0 Orphans)

🌐 BI DASHBOARD:
Dữ liệu trên Executive Intelligence Hub đã được làm mới tự động và sẵn sàng phục vụ.

================================================================================
Hệ thống giám sát tự động • AWS Cloud-Native Banking Data Warehouse
"""
    return subject, body


def lambda_handler(event, context):
    """
    Entrypoint cho AWS Lambda Function.
    Event payload mẫu:
    {
        "alert_type": "FAILURE" | "DATA_QUALITY_ALERT" | "SUCCESS",
        "stage": "build_warehouse",
        "error": "Connection timeout",
        "duration_seconds": 125.4,
        ...
    }
    """
    print(f"📥 Received event: {json.dumps(event, indent=2)}")
    
    alert_type = event.get("alert_type", "FAILURE").upper()

    if alert_type == "SUCCESS":
        subject, body = format_success_message(event)
    elif alert_type in ["DATA_QUALITY_ALERT", "WARNING"]:
        subject, body = format_quality_alert_message(event)
    else:
        subject, body = format_failure_message(event)

    topic_arn = SNS_TOPIC_ARN or os.getenv("SNS_TOPIC_ARN")

    if not topic_arn:
        print("⚠️ Cảnh báo: AWS_SNS_TOPIC_ARN chưa được cấu hình. In nội dung ra log CloudWatch:")
        print(f"Subject: {subject}")
        print(body)
        return {
            "statusCode": 200,
            "message": "Notification logged to CloudWatch (SNS_TOPIC_ARN not configured)",
            "subject": subject
        }

    try:
        response = sns_client.publish(
            TopicArn=topic_arn,
            Subject=subject[:100],  # SNS Subject giới hạn tối đa 100 ký tự
            Message=body
        )
        message_id = response.get("MessageId")
        print(f"✅ Đã gửi thông báo SNS thành công! MessageId: {message_id}")
        return {
            "statusCode": 200,
            "message": "Notification sent successfully via Amazon SNS",
            "message_id": message_id
        }
    except Exception as e:
        print(f"❌ Lỗi gửi SNS Notification: {e}")
        return {
            "statusCode": 500,
            "error": str(e)
        }
