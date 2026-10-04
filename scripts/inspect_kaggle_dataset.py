import os
from dotenv import load_dotenv

load_dotenv()

os.environ["KAGGLE_USERNAME"] = os.getenv("KAGGLE_USERNAME", "")
os.environ["KAGGLE_KEY"] = os.getenv("KAGGLE_KEY", "")

DATASET_NAME = "akrambelha/synthetic-banking-dataset-csv-sql-sqlite"

def inspect_dataset():
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    print("=" * 65)
    print(f"ĐANG QUÉT DANH SÁCH FILE CỦA DATASET: {DATASET_NAME}")
    print("=" * 65)

    # Liệt kê trực tiếp các file từ metadata của Kaggle
    files = api.dataset_list_files(DATASET_NAME).files
    for f in files:
        bytes_size = getattr(f, 'total_bytes', getattr(f, 'totalBytes', 'N/A'))
        print(f"- File trên Kaggle: {f.name} (Kích thước: {bytes_size} bytes)")

if __name__ == "__main__":
    inspect_dataset()
