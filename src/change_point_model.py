"""
change_point_model.py
=====================
Bayesian change point detection using PyMC.

Implements:
  1. Single change point model (simple mean shift)
  2. Multiple change point model (regime-switching means)
  3. Volatility change point model (variance shift)
"""

import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
import pytensor.tensor as pt
from typing import Optional


# ---------------------------------------------------------------------------
# 1. Single Change Point Model
# ---------------------------------------------------------------------------

def build_single_changepoint_model(
    prices: np.ndarray,
    n_obs: Optional[int] = None,
) -> pm.Model:
    """
    Build a Bayesian single change point model for oil price means.

    The model assumes the price series switches from mean μ₁ to mean μ₂
    at an unknown time index τ (tau), with shared standard deviation σ.

    Parameters
    ----------
    prices : np.ndarray
        1-D array of oil prices (USD/barrel).
    n_obs : int, optional
        Number of observations. Defaults to len(prices).

    Returns
    -------
    pm.Model
    """
    if n_obs is None:
        n_obs = len(prices)

    idx = np.arange(n_obs)

    with pm.Model() as model:
        # --- Priors ---
        # Switch point: discrete uniform over all time indices
        tau = pm.DiscreteUniform("tau", lower=0, upper=n_obs - 1)

        # Mean prices before and after the change point
        mu1 = pm.Normal("mu1", mu=np.mean(prices), sigma=30)
        mu2 = pm.Normal("mu2", mu=np.mean(prices), sigma=30)

        # Shared standard deviation
        sigma = pm.HalfNormal("sigma", sigma=20)

        # --- Likelihood ---
        # Switch function: mu1 for t < tau, mu2 for t >= tau
        mu = pm.math.switch(tau >= idx, mu1, mu2)
        obs = pm.Normal("obs", mu=mu, sigma=sigma, observed=prices)  # noqa: F841

    return model


def run_single_changepoint(
    prices: np.ndarray,
    draws: int = 2000,
    tune: int = 1000,
    chains: int = 2,
    random_seed: int = 42,
) -> tuple[pm.Model, az.InferenceData]:
    """
    Build and sample the single change point model.

    Returns
    -------
    model : pm.Model
    trace : az.InferenceData
    """
    model = build_single_changepoint_model(prices)
    with model:
        trace = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            random_seed=random_seed,
            return_inferencedata=True,
            progressbar=True,
            step=pm.Metropolis(),   # Discrete variable requires Metropolis
        )
    return model, trace


# ---------------------------------------------------------------------------
# 2. Multiple Change Point Model (up to K change points)
# ---------------------------------------------------------------------------

def build_multi_changepoint_model(
    prices: np.ndarray,
    n_segments: int = 3,
) -> pm.Model:
    """
    Build a Bayesian multiple change point model with (n_segments - 1) breaks.

    This uses a sorted vector of change points and assigns a mean to each
    segment. For efficiency the change points are modelled as cumulative
    fractions of the observation period.

    Parameters
    ----------
    prices     : 1-D array of prices.
    n_segments : Number of price regimes (breakpoints = n_segments - 1).

    Returns
    -------
    pm.Model
    """
    n_obs = len(prices)
    idx = np.arange(n_obs, dtype=float)

    with pm.Model() as model:
        # Segment means
        mu = pm.Normal("mu", mu=np.mean(prices), sigma=40, shape=n_segments)

        # Change points: sample fractions in (0,1), sort them
        # to guarantee ordering without explicit constraints
        cp_raw = pm.Uniform("cp_raw", lower=0.0, upper=1.0, shape=n_segments - 1)
        cp_sorted = pt.sort(cp_raw) * n_obs   # Convert fractions → indices

        sigma = pm.HalfNormal("sigma", sigma=20)

        # Build mean array via cumulative switches
        mean_vec = mu[0] * pt.ones(n_obs)
        for k in range(n_segments - 1):
            mean_vec = pt.switch(idx >= cp_sorted[k], mu[k + 1], mean_vec)

        obs = pm.Normal("obs", mu=mean_vec, sigma=sigma, observed=prices)  # noqa: F841

    return model


def run_multi_changepoint(
    prices: np.ndarray,
    n_segments: int = 3,
    draws: int = 2000,
    tune: int = 2000,
    chains: int = 2,
    target_accept: float = 0.9,
    random_seed: int = 42,
) -> tuple[pm.Model, az.InferenceData]:
    """Sample the multi-change-point model with NUTS."""
    model = build_multi_changepoint_model(prices, n_segments=n_segments)
    with model:
        trace = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            target_accept=target_accept,
            random_seed=random_seed,
            return_inferencedata=True,
            progressbar=True,
        )
    return model, trace


# ---------------------------------------------------------------------------
# 3. Utility: extract change point dates
# ---------------------------------------------------------------------------

def extract_changepoint_dates(
    trace: az.InferenceData,
    date_index: pd.DatetimeIndex,
    param_name: str = "tau",
) -> pd.Series:
    """
    Map posterior samples of tau (integer index) back to calendar dates.

    Parameters
    ----------
    trace      : ArviZ InferenceData object from sampling.
    date_index : DatetimeIndex of the price series.
    param_name : Name of the change point parameter in the trace.

    Returns
    -------
    pd.Series of datetime values (posterior samples mapped to dates).
    """
    tau_samples = trace.posterior[param_name].values.flatten().astype(int)
    # Clip to valid index range
    tau_samples = np.clip(tau_samples, 0, len(date_index) - 1)
    return pd.Series(date_index[tau_samples])


def summarise_changepoint(
    trace: az.InferenceData,
    date_index: pd.DatetimeIndex,
    param_name: str = "tau",
) -> dict:
    """
    Return a summary dict for a single change point parameter.

    Keys
    ----
    map_index   : MAP estimate (mode) of tau as integer index.
    map_date    : MAP estimate mapped to a calendar date.
    hdi_low     : 94% HDI lower bound (date).
    hdi_high    : 94% HDI upper bound (date).
    mu1_mean    : Posterior mean of mu1 (before).
    mu2_mean    : Posterior mean of mu2 (after).
    pct_change  : Percentage change from mu1 to mu2.
    """
    tau_flat = trace.posterior[param_name].values.flatten().astype(int)
    map_idx = int(pd.Series(tau_flat).mode().iloc[0])
    hdi = az.hdi(trace, var_names=[param_name], hdi_prob=0.94)
    low_idx = int(hdi[param_name].values[0])
    high_idx = int(hdi[param_name].values[1])

    mu1_mean = float(trace.posterior["mu1"].values.mean())
    mu2_mean = float(trace.posterior["mu2"].values.mean())
    pct = (mu2_mean - mu1_mean) / mu1_mean * 100

    return {
        "map_index": map_idx,
        "map_date": str(date_index[map_idx].date()),
        "hdi_low": str(date_index[low_idx].date()),
        "hdi_high": str(date_index[high_idx].date()),
        "mu1_mean": round(mu1_mean, 2),
        "mu2_mean": round(mu2_mean, 2),
        "pct_change": round(pct, 1),
    }


def compare_models(
    models: list[pm.Model],
    traces: list[az.InferenceData],
    model_names: list[str],
) -> pd.DataFrame:
    """
    Compare multiple PyMC models using LOO (leave-one-out cross-validation).

    Returns
    -------
    pd.DataFrame with ELPD_LOO, SE, ELPD_diff, weight columns.
    """
    compare_dict = {name: tr for name, tr in zip(model_names, traces)}
    comparison = az.compare(compare_dict, ic="loo")
    return comparison
