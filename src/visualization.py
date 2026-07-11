"""
visualization.py
================
Reusable plotting utilities for Brent oil price change point analysis.
All functions return matplotlib Figure objects so callers can save or display them.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import arviz as az
from typing import Optional

# ---------------------------------------------------------------------------
# Global style
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "figure.dpi": 120,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.family": "sans-serif",
    "axes.titlesize": 13,
    "axes.labelsize": 11,
})
PALETTE = ["#2196F3", "#FF5722", "#4CAF50", "#9C27B0", "#FF9800"]


# ---------------------------------------------------------------------------
# 1. Raw price series
# ---------------------------------------------------------------------------

def plot_price_series(
    df: pd.DataFrame,
    price_col: str = "Price",
    events_df: Optional[pd.DataFrame] = None,
    title: str = "Brent Crude Oil Price (USD/barrel)",
) -> plt.Figure:
    """
    Plot the raw Brent oil price time series with optional event markers.

    Parameters
    ----------
    df        : DataFrame with DatetimeIndex and a Price column.
    events_df : Optional DataFrame with EventDate and EventName columns.
    """
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(df.index, df[price_col], color=PALETTE[0], linewidth=0.9, alpha=0.9)
    ax.fill_between(df.index, df[price_col], alpha=0.1, color=PALETTE[0])

    if events_df is not None:
        for _, row in events_df.iterrows():
            ed = row["EventDate"]
            if df.index.min() <= ed <= df.index.max():
                ax.axvline(ed, color=PALETTE[1], alpha=0.5, linewidth=0.8, linestyle="--")
                ax.text(ed, df[price_col].max() * 0.97, row["EventName"],
                        rotation=90, fontsize=6.5, va="top", color=PALETTE[1])

    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD/barrel)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 2. Log returns
# ---------------------------------------------------------------------------

def plot_log_returns(
    df: pd.DataFrame,
    log_col: str = "LogReturn",
    vol_col: str = "RollingStd30",
    title: str = "Brent Oil Log Returns & Rolling Volatility (30-day)",
) -> plt.Figure:
    """
    Two-panel figure: log returns + rolling volatility.
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 7), sharex=True)

    ax1.plot(df.index, df[log_col], color=PALETTE[0], linewidth=0.6, alpha=0.8)
    ax1.axhline(0, color="gray", linewidth=0.5)
    ax1.set_title("Daily Log Returns")
    ax1.set_ylabel("Log Return")

    ax2.plot(df.index, df[vol_col], color=PALETTE[1], linewidth=0.9)
    ax2.set_title("30-day Rolling Volatility (Std of Log Returns)")
    ax2.set_ylabel("Volatility")
    ax2.set_xlabel("Date")

    for ax in (ax1, ax2):
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.xaxis.set_major_locator(mdates.YearLocator(5))

    fig.suptitle(title, fontsize=14, y=1.01)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 3. Posterior of tau (single change point)
# ---------------------------------------------------------------------------

def plot_tau_posterior(
    trace,
    date_index: pd.DatetimeIndex,
    title: str = "Posterior Distribution of Change Point (τ)",
) -> plt.Figure:
    """
    Histogram of posterior samples for the switch point τ mapped to dates.
    """
    tau_samples = trace.posterior["tau"].values.flatten().astype(int)
    tau_samples = np.clip(tau_samples, 0, len(date_index) - 1)
    tau_dates = date_index[tau_samples]

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.hist(
        [d.toordinal() for d in tau_dates],
        bins=80,
        color=PALETTE[2],
        edgecolor="white",
        linewidth=0.3,
    )

    # Map x ticks back to year labels
    date_range = pd.date_range(date_index.min(), date_index.max(), freq="5YS")
    ax.set_xticks([d.toordinal() for d in date_range])
    ax.set_xticklabels([d.strftime("%Y") for d in date_range])

    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Posterior Sample Count")
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 4. Before / after posteriors
# ---------------------------------------------------------------------------

def plot_mu_posteriors(
    trace,
    title: str = "Posterior Distributions: Mean Price Before & After Change Point",
) -> plt.Figure:
    """
    Overlapping KDE plots of mu1 (before) and mu2 (after).
    """
    mu1 = trace.posterior["mu1"].values.flatten()
    mu2 = trace.posterior["mu2"].values.flatten()

    fig, ax = plt.subplots(figsize=(9, 4))
    sns.kdeplot(mu1, ax=ax, label="μ₁ (Before)", color=PALETTE[0], fill=True, alpha=0.35)
    sns.kdeplot(mu2, ax=ax, label="μ₂ (After)", color=PALETTE[1], fill=True, alpha=0.35)

    ax.axvline(mu1.mean(), color=PALETTE[0], linestyle="--", linewidth=1.2)
    ax.axvline(mu2.mean(), color=PALETTE[1], linestyle="--", linewidth=1.2)

    ax.set_title(title)
    ax.set_xlabel("Price (USD/barrel)")
    ax.set_ylabel("Density")
    ax.legend()
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 5. Trace plots (convergence diagnostics)
# ---------------------------------------------------------------------------

def plot_traces(trace, var_names: list[str] = None) -> plt.Figure:
    """Wrapper around az.plot_trace for convergence diagnostics."""
    ax_array = az.plot_trace(trace, var_names=var_names, combined=False)
    fig = ax_array.ravel()[0].figure
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 6. Annotated price series with detected change points
# ---------------------------------------------------------------------------

def plot_price_with_changepoints(
    df: pd.DataFrame,
    changepoint_dates: list[str | pd.Timestamp],
    segment_means: list[float],
    events_df: Optional[pd.DataFrame] = None,
    title: str = "Brent Oil Price with Detected Change Points",
) -> plt.Figure:
    """
    Plot price series with vertical change point lines and horizontal
    segment mean lines.

    Parameters
    ----------
    changepoint_dates : list of detected CP dates (strings or Timestamps).
    segment_means     : list of posterior mean prices per segment.
    """
    cp_dates = [pd.Timestamp(d) for d in changepoint_dates]
    fig, ax = plt.subplots(figsize=(15, 5))
    ax.plot(df.index, df["Price"], color="#BDBDBD", linewidth=0.7, alpha=0.9)

    boundaries = [df.index.min()] + cp_dates + [df.index.max()]
    colors = PALETTE[:len(segment_means)]

    for i, (start, end, mean_val, color) in enumerate(
        zip(boundaries[:-1], boundaries[1:], segment_means, colors)
    ):
        seg = df.loc[start:end]
        ax.plot(seg.index, seg["Price"], color=color, linewidth=1.1, alpha=0.85)
        ax.hlines(mean_val, start, end, colors=color, linestyles="--",
                  linewidth=1.4, label=f"Regime {i+1}: μ=${mean_val:.1f}")

    for cp in cp_dates:
        ax.axvline(cp, color="black", linestyle=":", linewidth=1.2)
        ax.text(cp, df["Price"].max() * 0.98, cp.strftime("%Y-%m"),
                rotation=90, fontsize=7.5, va="top")

    if events_df is not None:
        for _, row in events_df.iterrows():
            ed = row["EventDate"]
            if df.index.min() <= ed <= df.index.max():
                ax.axvline(ed, color="#E91E63", alpha=0.35, linewidth=0.7)

    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD/barrel)")
    ax.legend(fontsize=8, loc="upper left")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 7. Event impact bar chart
# ---------------------------------------------------------------------------

def plot_event_impact(
    events: list[dict],
    title: str = "Estimated Price Impact of Key Events",
) -> plt.Figure:
    """
    Horizontal bar chart of percentage price changes around key events.

    Parameters
    ----------
    events : list of dicts with keys: name, pct_change, direction ('up'/'down')
    """
    names = [e["name"] for e in events]
    pcts = [e["pct_change"] for e in events]
    colors = [PALETTE[2] if p > 0 else PALETTE[1] for p in pcts]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(names, pcts, color=colors, edgecolor="white")
    ax.axvline(0, color="black", linewidth=0.8)

    for bar, pct in zip(bars, pcts):
        xpos = pct + (1 if pct >= 0 else -1)
        ax.text(xpos, bar.get_y() + bar.get_height() / 2,
                f"{pct:+.1f}%", va="center", fontsize=8.5,
                color="black")

    ax.set_title(title)
    ax.set_xlabel("Price Change (%)")
    fig.tight_layout()
    return fig
