"""
Unit tests for src/data_loader.py
"""

import pytest
import pandas as pd
import numpy as np
from io import StringIO
from unittest.mock import patch
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.data_loader import (
    load_brent_prices,
    compute_log_returns,
    get_time_index,
    split_around_event,
    summarise_period,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_CSV = """Date,Price
20-May-87,18.63
21-May-87,18.45
22-May-87,18.55
25-May-87,18.72
26-May-87,19.01
27-May-87,18.90
28-May-87,19.15
29-May-87,19.30
01-Jun-87,19.22
02-Jun-87,19.45
"""


@pytest.fixture
def sample_df():
    """Load a small in-memory price DataFrame."""
    df = pd.read_csv(StringIO(SAMPLE_CSV))
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, infer_datetime_format=True)
    df = df.sort_values("Date").set_index("Date")
    df["Price"] = pd.to_numeric(df["Price"])
    df["LogReturn"] = np.log(df["Price"]).diff()
    df["RollingStd30"] = df["LogReturn"].rolling(window=5, min_periods=2).std()
    return df


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestComputeLogReturns:
    def test_returns_series(self, sample_df):
        lr = compute_log_returns(sample_df["Price"])
        assert isinstance(lr, pd.Series)

    def test_length_is_n_minus_1(self, sample_df):
        lr = compute_log_returns(sample_df["Price"])
        assert len(lr) == len(sample_df) - 1

    def test_no_nan(self, sample_df):
        lr = compute_log_returns(sample_df["Price"])
        assert not lr.isna().any()

    def test_values_finite(self, sample_df):
        lr = compute_log_returns(sample_df["Price"])
        assert np.isfinite(lr.values).all()


class TestGetTimeIndex:
    def test_starts_at_zero(self, sample_df):
        idx = get_time_index(sample_df)
        assert idx[0] == 0

    def test_correct_length(self, sample_df):
        idx = get_time_index(sample_df)
        assert len(idx) == len(sample_df)

    def test_consecutive(self, sample_df):
        idx = get_time_index(sample_df)
        assert np.all(np.diff(idx) == 1)


class TestSplitAroundEvent:
    def test_before_is_nonempty(self, sample_df):
        before, after = split_around_event(sample_df, "1987-05-27", window_days=5)
        assert len(before) > 0

    def test_after_is_nonempty(self, sample_df):
        before, after = split_around_event(sample_df, "1987-05-27", window_days=5)
        assert len(after) > 0

    def test_before_comes_before_event(self, sample_df):
        event = pd.Timestamp("1987-05-27")
        before, _ = split_around_event(sample_df, event, window_days=5)
        assert before.index.max() <= event

    def test_after_comes_after_event(self, sample_df):
        event = pd.Timestamp("1987-05-27")
        _, after = split_around_event(sample_df, event, window_days=5)
        assert after.index.min() >= event


class TestSummarisePeriod:
    def test_keys_present(self, sample_df):
        summary = summarise_period(sample_df["Price"])
        for key in ("mean", "median", "std", "min", "max", "n_obs"):
            assert key in summary

    def test_n_obs_correct(self, sample_df):
        summary = summarise_period(sample_df["Price"])
        assert summary["n_obs"] == len(sample_df)

    def test_mean_in_range(self, sample_df):
        summary = summarise_period(sample_df["Price"])
        assert summary["min"] <= summary["mean"] <= summary["max"]
