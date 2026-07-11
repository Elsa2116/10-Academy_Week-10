"""
Unit tests for src/change_point_model.py
(Tests that don't require MCMC sampling – structural / smoke tests only)
"""

import pytest
import numpy as np
import pymc as pm
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.change_point_model import (
    build_single_changepoint_model,
    build_multi_changepoint_model,
    summarise_changepoint,
    extract_changepoint_dates,
)


# ---------------------------------------------------------------------------
# Synthetic price data
# ---------------------------------------------------------------------------

@pytest.fixture
def synthetic_prices():
    """Simple two-regime price series: mean 30 then mean 70."""
    rng = np.random.default_rng(0)
    before = rng.normal(loc=30, scale=3, size=200)
    after = rng.normal(loc=70, scale=5, size=200)
    return np.concatenate([before, after])


# ---------------------------------------------------------------------------
# Model structure tests (no sampling)
# ---------------------------------------------------------------------------

class TestSingleChangepointModel:
    def test_model_builds(self, synthetic_prices):
        model = build_single_changepoint_model(synthetic_prices)
        assert isinstance(model, pm.Model)

    def test_model_has_tau(self, synthetic_prices):
        model = build_single_changepoint_model(synthetic_prices)
        assert "tau" in [v.name for v in model.free_RVs]

    def test_model_has_mu1_mu2(self, synthetic_prices):
        model = build_single_changepoint_model(synthetic_prices)
        names = [v.name for v in model.free_RVs]
        assert "mu1" in names
        assert "mu2" in names

    def test_model_has_sigma(self, synthetic_prices):
        model = build_single_changepoint_model(synthetic_prices)
        names = [v.name for v in model.free_RVs]
        assert "sigma" in names

    def test_model_n_free_rvs(self, synthetic_prices):
        model = build_single_changepoint_model(synthetic_prices)
        # tau, mu1, mu2, sigma = 4 free RVs
        assert len(model.free_RVs) == 4

    def test_short_series(self):
        """Model should build even for very short series."""
        prices = np.array([10.0, 11.0, 50.0, 51.0, 52.0])
        model = build_single_changepoint_model(prices)
        assert isinstance(model, pm.Model)


class TestMultiChangepointModel:
    def test_model_builds_k3(self, synthetic_prices):
        model = build_multi_changepoint_model(synthetic_prices, n_segments=3)
        assert isinstance(model, pm.Model)

    def test_model_builds_k2(self, synthetic_prices):
        model = build_multi_changepoint_model(synthetic_prices, n_segments=2)
        assert isinstance(model, pm.Model)

    def test_mu_shape_k3(self, synthetic_prices):
        model = build_multi_changepoint_model(synthetic_prices, n_segments=3)
        mu_var = next(v for v in model.free_RVs if v.name == "mu")
        assert mu_var.shape.eval()[0] == 3

    def test_cp_raw_shape_k3(self, synthetic_prices):
        model = build_multi_changepoint_model(synthetic_prices, n_segments=3)
        cp_var = next(v for v in model.free_RVs if v.name == "cp_raw")
        assert cp_var.shape.eval()[0] == 2   # n_segments - 1 = 2


# ---------------------------------------------------------------------------
# Utility function tests
# ---------------------------------------------------------------------------

class TestExtractChangepointDates:
    def test_returns_series(self, synthetic_prices):
        import pandas as pd
        # Minimal fake trace
        class FakeTrace:
            class posterior:
                tau = type("T", (), {"values": np.array([[[100, 110, 120]]])}  )()
        date_index = pd.date_range("2000-01-01", periods=400, freq="D")
        result = extract_changepoint_dates(FakeTrace(), date_index, param_name="tau")
        assert isinstance(result, pd.Series)
        assert len(result) == 3
