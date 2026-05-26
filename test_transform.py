"""
tests/test_transform.py
Unit tests for the transform/process.py cleaning logic.
"""

import pandas as pd
import pytest
from datetime import datetime
from transform.process import clean


def make_df(**overrides):
    """Build a minimal valid DataFrame row for testing."""
    base = {
        "tpep_pickup_datetime": [datetime(2024, 1, 15, 9, 0, 0)],
        "tpep_dropoff_datetime": [datetime(2024, 1, 15, 9, 20, 0)],
        "fare_amount": [12.50],
        "PULocationID": [161],
        "DOLocationID": [239],
    }
    base.update({k: [v] for k, v in overrides.items()})
    return pd.DataFrame(base)


def test_clean_valid_row():
    result = clean(make_df())
    assert len(result) == 1
    assert result.iloc[0]["trip_duration_min"] == pytest.approx(20.0)


def test_clean_removes_negative_fare():
    assert len(clean(make_df(fare_amount=-5.0))) == 0


def test_clean_removes_zero_fare():
    assert len(clean(make_df(fare_amount=0.0))) == 0


def test_clean_removes_implausible_duration():
    # 5-hour trip exceeds 240-min threshold
    assert len(clean(make_df(tpep_dropoff_datetime=datetime(2024, 1, 15, 14, 0, 0)))) == 0


def test_clean_adds_derived_columns():
    result = clean(make_df())
    for col in ["pickup_date", "pickup_hour", "pickup_year", "pickup_month"]:
        assert col in result.columns
    assert result.iloc[0]["pickup_hour"] == 9
    assert result.iloc[0]["pickup_year"] == 2024
