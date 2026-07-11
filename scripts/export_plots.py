"""
export_plots.py
===============
Generate the final submission plot images without re-running Bayesian sampling.

This script uses the checked-in Brent price data, the event catalogue, and the
precomputed results JSON to produce PNG figures in outputs/.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
import matplotlib.dates as mdates
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import load_brent_prices, load_key_events


PALETTE = ["#2196F3", "#FF5722", "#4CAF50", "#9C27B0", "#FF9800"]


def plot_price_series(df: pd.DataFrame, events_df: pd.DataFrame | None = None) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(df.index, df["Price"], color=PALETTE[0], linewidth=0.9, alpha=0.9)
    ax.fill_between(df.index, df["Price"], alpha=0.1, color=PALETTE[0])

    if events_df is not None:
        for _, row in events_df.iterrows():
            ed = row["EventDate"]
            if df.index.min() <= ed <= df.index.max():
                ax.axvline(ed, color=PALETTE[1], alpha=0.35, linewidth=0.7, linestyle="--")

    ax.set_title("Brent Crude Oil Price (USD/barrel)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD/barrel)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    fig.tight_layout()
    return fig


def plot_log_returns(df: pd.DataFrame) -> plt.Figure:
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 7), sharex=True)

    ax1.plot(df.index, df["LogReturn"], color=PALETTE[0], linewidth=0.6, alpha=0.8)
    ax1.axhline(0, color="gray", linewidth=0.5)
    ax1.set_title("Daily Log Returns")
    ax1.set_ylabel("Log Return")

    ax2.plot(df.index, df["RollingStd30"], color=PALETTE[1], linewidth=0.9)
    ax2.set_title("30-day Rolling Volatility (Std of Log Returns)")
    ax2.set_ylabel("Volatility")
    ax2.set_xlabel("Date")

    for ax in (ax1, ax2):
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.xaxis.set_major_locator(mdates.YearLocator(5))

    fig.suptitle("Brent Oil Log Returns & Rolling Volatility (30-day)", fontsize=14, y=1.01)
    fig.tight_layout()
    return fig


def plot_price_with_changepoints(
    df: pd.DataFrame,
    changepoint_dates: list[str],
    segment_means: list[float],
    events_df: pd.DataFrame | None = None,
) -> plt.Figure:
    cp_dates = [pd.Timestamp(d) for d in changepoint_dates]
    fig, ax = plt.subplots(figsize=(15, 5))
    ax.plot(df.index, df["Price"], color="#BDBDBD", linewidth=0.7, alpha=0.9)

    boundaries = [df.index.min()] + cp_dates + [df.index.max()]
    colors = PALETTE[:len(segment_means)]

    for start, end, mean_val, color in zip(boundaries[:-1], boundaries[1:], segment_means, colors):
        seg = df.loc[start:end]
        ax.plot(seg.index, seg["Price"], color=color, linewidth=1.1, alpha=0.85)
        ax.hlines(mean_val, start, end, colors=color, linestyles="--", linewidth=1.4)

    for cp in cp_dates:
        ax.axvline(cp, color="black", linestyle=":", linewidth=1.2)

    if events_df is not None:
        for _, row in events_df.iterrows():
            ed = row["EventDate"]
            if df.index.min() <= ed <= df.index.max():
                ax.axvline(ed, color="#E91E63", alpha=0.18, linewidth=0.7)

    ax.set_title("Brent Oil Price with Detected Change Points")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD/barrel)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    fig.tight_layout()
    return fig


def plot_event_impact(events: list[dict]) -> plt.Figure:
    names = [e["name"] for e in events]
    pcts = [e["pct_change"] for e in events]
    colors = [PALETTE[2] if p > 0 else PALETTE[1] for p in pcts]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(names, pcts, color=colors, edgecolor="white")
    ax.axvline(0, color="black", linewidth=0.8)

    for bar, pct in zip(bars, pcts):
        xpos = pct + (1 if pct >= 0 else -1)
        ax.text(xpos, bar.get_y() + bar.get_height() / 2, f"{pct:+.1f}%", va="center", fontsize=8.5)

    ax.set_title("Estimated Price Impact of Key Events")
    ax.set_xlabel("Price Change (%)")
    fig.tight_layout()
    return fig


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    out_dir = repo_root / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    prices = load_brent_prices(repo_root / "data" / "brent_oil_prices.csv")
    events = load_key_events(repo_root / "data" / "key_events.csv")
    results = json.loads((out_dir / "results.json").read_text(encoding="utf-8"))

    change_points = sorted(results["change_points"], key=lambda item: item["date"])
    cp_dates = [item["date"] for item in change_points]
    segment_means = [change_points[0]["mu_before"]] + [item["mu_after"] for item in change_points]

    event_impacts = [
        {"name": item["label"], "pct_change": item["pct_change"]}
        for item in change_points
    ]

    fig1 = plot_price_series(prices, events_df=events)
    fig1.savefig(out_dir / "fig_01_price_series.png", dpi=160, bbox_inches="tight")

    fig2 = plot_log_returns(prices)
    fig2.savefig(out_dir / "fig_02_log_returns.png", dpi=160, bbox_inches="tight")

    fig3 = plot_price_with_changepoints(prices, cp_dates, segment_means, events_df=events)
    fig3.savefig(out_dir / "fig_03_change_points.png", dpi=160, bbox_inches="tight")

    fig4 = plot_event_impact(event_impacts)
    fig4.savefig(out_dir / "fig_04_event_impact.png", dpi=160, bbox_inches="tight")

    for fig in (fig1, fig2, fig3, fig4):
        plt.close(fig)

    print("Saved plots to", out_dir)


if __name__ == "__main__":
    main()