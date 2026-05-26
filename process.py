"""
transform/process.py

Reads raw Parquet files from S3, cleans and enriches the data,
then writes partitioned Parquet back to S3 for Athena querying.
"""

import os
import logging
import boto3
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

S3_BUCKET = os.environ["S3_BUCKET_NAME"]
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")


def read_parquet_from_s3(s3_key: str) -> pd.DataFrame:
    s3 = boto3.client("s3", region_name=AWS_REGION)
    logger.info(f"Reading s3://{S3_BUCKET}/{s3_key}")
    obj = s3.get_object(Bucket=S3_BUCKET, Key=s3_key)
    return pd.read_parquet(BytesIO(obj["Body"].read()))


def clean(df: pd.DataFrame) -> pd.DataFrame:
    # Drop nulls in key columns
    df = df.dropna(subset=["tpep_pickup_datetime", "tpep_dropoff_datetime", "fare_amount"])

    # Remove negative fares and implausible trip durations
    df = df[df["fare_amount"] > 0]
    df["trip_duration_min"] = (
        df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]
    ).dt.total_seconds() / 60
    df = df[(df["trip_duration_min"] > 0) & (df["trip_duration_min"] < 240)]

    # Add derived columns for partitioning and analytics
    df["pickup_date"] = df["tpep_pickup_datetime"].dt.date
    df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour
    df["pickup_year"] = df["tpep_pickup_datetime"].dt.year
    df["pickup_month"] = df["tpep_pickup_datetime"].dt.month

    return df


def write_parquet_to_s3(df: pd.DataFrame, year: int, month: int) -> None:
    s3_key = f"processed/year={year}/month={month:02d}/data.parquet"
    buffer = BytesIO()
    table = pa.Table.from_pandas(df)
    pq.write_table(table, buffer, compression="snappy")
    buffer.seek(0)

    s3 = boto3.client("s3", region_name=AWS_REGION)
    logger.info(f"Writing processed data → s3://{S3_BUCKET}/{s3_key}")
    s3.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=buffer.getvalue())
    logger.info(f"Done. Rows written: {len(df):,}")


def process(year: int, month: int) -> None:
    raw_key = f"raw/{year}/{month:02d}/yellow_tripdata_{year}-{month:02d}.parquet"
    df = read_parquet_from_s3(raw_key)
    logger.info(f"Raw rows: {len(df):,}")
    df = clean(df)
    logger.info(f"Clean rows: {len(df):,}")
    write_parquet_to_s3(df, year, month)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Transform raw taxi data and write Parquet to S3")
    parser.add_argument("--year", type=int, default=2024)
    parser.add_argument("--month", type=int, default=1)
    args = parser.parse_args()

    process(args.year, args.month)
