"""
dashboard/queries.py

Helpers to run Athena queries and return results as DataFrames.
"""

import os
import time
import logging
import boto3
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

ATHENA_DATABASE = os.environ.get("ATHENA_DATABASE", "nyc_taxi")
ATHENA_OUTPUT = os.environ["ATHENA_OUTPUT_BUCKET"]
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")


def run_query(sql: str) -> pd.DataFrame:
    """Execute a SQL query in Athena and return results as a DataFrame."""
    client = boto3.client("athena", region_name=AWS_REGION)

    response = client.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={"Database": ATHENA_DATABASE},
        ResultConfiguration={"OutputLocation": ATHENA_OUTPUT},
    )
    query_id = response["QueryExecutionId"]
    logger.info(f"Athena query started: {query_id}")

    # Poll until complete
    while True:
        status = client.get_query_execution(QueryExecutionId=query_id)
        state = status["QueryExecution"]["Status"]["State"]
        if state in ("SUCCEEDED", "FAILED", "CANCELLED"):
            break
        time.sleep(1)

    if state != "SUCCEEDED":
        reason = status["QueryExecution"]["Status"].get("StateChangeReason", "Unknown")
        raise RuntimeError(f"Athena query {state}: {reason}")

    # Fetch results
    paginator = client.get_paginator("get_query_results")
    rows, headers = [], None
    for page in paginator.paginate(QueryExecutionId=query_id):
        result_rows = page["ResultSet"]["Rows"]
        if headers is None:
            headers = [col["VarCharValue"] for col in result_rows[0]["Data"]]
            result_rows = result_rows[1:]
        for row in result_rows:
            rows.append([col.get("VarCharValue", "") for col in row["Data"]])

    return pd.DataFrame(rows, columns=headers)


# --- Pre-built queries ---

TRIPS_BY_DAY = """
SELECT
    pickup_date,
    COUNT(*) AS trip_count,
    ROUND(AVG(fare_amount), 2) AS avg_fare,
    ROUND(AVG(trip_duration_min), 1) AS avg_duration_min
FROM nyc_taxi_processed
WHERE pickup_year = 2024 AND pickup_month = 1
GROUP BY pickup_date
ORDER BY pickup_date
"""

TRIPS_BY_HOUR = """
SELECT
    pickup_hour,
    COUNT(*) AS trip_count,
    ROUND(AVG(fare_amount), 2) AS avg_fare
FROM nyc_taxi_processed
WHERE pickup_year = 2024 AND pickup_month = 1
GROUP BY pickup_hour
ORDER BY pickup_hour
"""

TOP_ZONES = """
SELECT
    PULocationID AS zone_id,
    COUNT(*) AS pickups
FROM nyc_taxi_processed
WHERE pickup_year = 2024 AND pickup_month = 1
GROUP BY PULocationID
ORDER BY pickups DESC
LIMIT 10
"""
