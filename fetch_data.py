"""
ingestion/fetch_data.py

Downloads NYC TLC Yellow Taxi trip data for a given year/month
and uploads the raw CSV to S3.
"""

import os
import logging
import requests
import boto3
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

S3_BUCKET = os.environ["S3_BUCKET_NAME"]
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

# NYC TLC data is hosted on a public S3 bucket
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"


def build_url(year: int, month: int) -> str:
    return f"{BASE_URL}/yellow_tripdata_{year}-{month:02d}.parquet"


def upload_to_s3(local_path: str, s3_key: str) -> None:
    s3 = boto3.client("s3", region_name=AWS_REGION)
    logger.info(f"Uploading {local_path} → s3://{S3_BUCKET}/{s3_key}")
    s3.upload_file(local_path, S3_BUCKET, s3_key)
    logger.info("Upload complete.")


def fetch_and_upload(year: int, month: int) -> None:
    url = build_url(year, month)
    filename = f"yellow_tripdata_{year}-{month:02d}.parquet"
    s3_key = f"raw/{year}/{month:02d}/{filename}"

    logger.info(f"Fetching: {url}")
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()

    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    logger.info(f"Downloaded {filename} ({os.path.getsize(filename) / 1e6:.1f} MB)")
    upload_to_s3(filename, s3_key)
    os.remove(filename)


if __name__ == "__main__":
    # Default: fetch last 3 months of data
    import argparse

    parser = argparse.ArgumentParser(description="Fetch NYC Taxi data and upload to S3")
    parser.add_argument("--year", type=int, default=2024)
    parser.add_argument("--month", type=int, default=1)
    args = parser.parse_args()

    fetch_and_upload(args.year, args.month)
