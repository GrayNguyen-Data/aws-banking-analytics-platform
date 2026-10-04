"""
Unit tests for data cleaning logic in clean_load_staging
"""

import pandas as pd
from scripts.clean_load_staging import clean_dataframe


def test_clean_dataframe_strip_whitespace():
    raw_data = {
        "customer_id": [" C1001 ", "C1002  "],
        "first_name": [" John ", " Jane "],
        "email": [" john@example.com ", "jane@example.com "]
    }
    config = {"columns": ["customer_id", "first_name", "email"]}
    df = pd.DataFrame(raw_data)
    cleaned_df = clean_dataframe(df, config)

    assert cleaned_df["customer_id"].iloc[0] == "C1001"
    assert cleaned_df["first_name"].iloc[1] == "Jane"
    assert cleaned_df["email"].iloc[0] == "john@example.com"


def test_clean_dataframe_date_formatting():
    raw_data = {
        "account_id": ["A1", "A2"],
        "open_date": ["2022/01/15", "15-08-2023"]
    }
    config = {
        "columns": ["account_id", "open_date"],
        "date_cols": ["open_date"]
    }
    df = pd.DataFrame(raw_data)
    cleaned_df = clean_dataframe(df, config)

    assert cleaned_df["open_date"].iloc[0] == "2022-01-15"
    assert cleaned_df["open_date"].iloc[1] == "2023-08-15"


def test_clean_dataframe_datetime_formatting():
    raw_data = {
        "transaction_id": ["TX100"],
        "transaction_date": ["2023-05-10 14:30:00.123456"]
    }
    config = {
        "columns": ["transaction_id", "transaction_date"],
        "datetime_cols": ["transaction_date"]
    }
    df = pd.DataFrame(raw_data)
    cleaned_df = clean_dataframe(df, config)

    assert cleaned_df["transaction_date"].iloc[0] == "2023-05-10 14:30:00"
