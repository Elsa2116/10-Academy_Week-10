"""
run_analysis.py
===============
CLI runner for the Brent oil change point analysis pipeline.
Loads data, fits Bayesian change point models, saves figures and results.

Usage:
    python scripts/run_analysis.py --data data/brent_oil_prices.csv \
                                   --events data/key_events.csv \
                                   --output outputs/ \
                                   --segments 4
"""

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")   # Non-interactive backend for headless runs
import matplotlib.pyplot as plt

# Make src importable from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import load_brent_prices, load_key_events, summarise_period
from src.change_point_model import (
    run_single_changepoint,
    run_multi_changepoint,
    summarise_changepoint,
)
from src.visualization import (
    plot_price_series,
    plot_log_returns,
    plot_tau_posterior,
    plot_mu_posteriors,
    plot_price_with_changepoints,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Brent Oil Change Point Analysis")
    parser.add_argument("--data", default="data/brent_oil_prices.csv",
                        help="Path to Brent price CSV")
    parser.add_argument("--events", default="data/key_events.csv",
                        help="Path to key events CSV")
    parser.add_argument("--output", default="outputs/",
                        help="Output directory for figures and results JSON")
    parser.add_argument("--segments", type=int, default=4,
                        help="Number of price regimes for multi-CP model (default 4)")
    parser.add_argument("--draws", type=int, default=2000,
                        help="MCMC draws per chain")
    parser.add_argument("--tune", type=int, default=2000,
                        help="MCMC tuning steps")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed")
    return parser.parse_args()


def main():
    args = parse_args()
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Brent Oil Price Change Point Analysis")
    print("Birhan Energies – July 2026")
    print("=" * 60)

    # ------------------------------------------------------------------
    # 1. Load data
    # ------------------------------------------------------------------
    print("\n[1/6] Loading data …")
    df = load_brent_prices(args.data)
    events_df = load_key_events(args.events)
    print(f"  Loaded {len(df):,} daily observations ({df.index.min().date()} – {df.index.max().date()})")
    print(f"  Loaded {len(events_df)} key events")

    # ------------------------------------------------------------------
    # 2. EDA figures
    # ------------------------------------------------------------------
    print("\n[2/6] Generating EDA figures …")
    fig_price = plot_price_series(df, events_df=events_df)
    fig_price.savefig(out_dir / "fig_01_price_series.png", dpi=150, bbox_inches="tight")
    plt.close(fig_price)

    fig_lr = plot_log_returns(df)
    fig_lr.savefig(out_dir / "fig_02_log_returns.png", dpi=150, bbox_inches="tight")
    plt.close(fig_lr)

    # ------------------------------------------------------------------
    # 3. Single change point model
    # ------------------------------------------------------------------
    print("\n[3/6] Fitting single change point model (Metropolis MCMC) …")
    prices = df["Price"].values
    model_1cp, trace_1cp = run_single_changepoint(
        prices, draws=args.draws, tune=args.tune, random_seed=args.seed
    )
    summary_1cp = summarise_changepoint(trace_1cp, df.index)
    print(f"  MAP change point: {summary_1cp['map_date']}")
    print(f"  μ₁ (before): ${summary_1cp['mu1_mean']:.2f}  →  μ₂ (after): ${summary_1cp['mu2_mean']:.2f}  ({summary_1cp['pct_change']:+.1f}%)")

    fig_tau = plot_tau_posterior(trace_1cp, df.index)
    fig_tau.savefig(out_dir / "fig_03_tau_posterior.png", dpi=150, bbox_inches="tight")
    plt.close(fig_tau)

    fig_mu = plot_mu_posteriors(trace_1cp)
    fig_mu.savefig(out_dir / "fig_04_mu_posteriors.png", dpi=150, bbox_inches="tight")
    plt.close(fig_mu)

    # ------------------------------------------------------------------
    # 4. Multi change point model
    # ------------------------------------------------------------------
    print(f"\n[4/6] Fitting {args.segments}-segment change point model (NUTS) …")
    model_mcp, trace_mcp = run_multi_changepoint(
        prices,
        n_segments=args.segments,
        draws=args.draws,
        tune=args.tune,
        random_seed=args.seed,
    )

    # Extract segment means and change point dates
    cp_fractions = trace_mcp.posterior["cp_raw"].values.mean(axis=(0, 1))
    cp_fractions_sorted = np.sort(cp_fractions)
    cp_indices = (cp_fractions_sorted * len(prices)).astype(int)
    cp_dates = [str(df.index[int(np.clip(i, 0, len(df)-1))].date()) for i in cp_indices]
    seg_means = trace_mcp.posterior["mu"].values.mean(axis=(0, 1)).tolist()

    print(f"  Detected change points: {cp_dates}")

    fig_mcp = plot_price_with_changepoints(df, cp_dates, seg_means, events_df=events_df)
    fig_mcp.savefig(out_dir / "fig_05_multi_changepoints.png", dpi=150, bbox_inches="tight")
    plt.close(fig_mcp)

    # ------------------------------------------------------------------
    # 5. Save JSON results
    # ------------------------------------------------------------------
    print("\n[5/6] Saving results JSON …")
    results = {
        "metadata": {
            "n_observations": len(df),
            "date_range": [str(df.index.min().date()), str(df.index.max().date())],
            "n_events": len(events_df),
        },
        "single_changepoint": summary_1cp,
        "multi_changepoint": {
            "n_segments": args.segments,
            "change_point_dates": cp_dates,
            "segment_means": [round(m, 2) for m in seg_means],
        },
        "overall_stats": summarise_period(df["Price"]),
    }
    with open(out_dir / "results.json", "w") as f:
        json.dump(results, f, indent=2)

    # ------------------------------------------------------------------
    # 6. Summary
    # ------------------------------------------------------------------
    print("\n[6/6] Analysis complete.")
    print(f"  Figures saved to:  {out_dir}/")
    print(f"  Results JSON:      {out_dir}/results.json")
    print("\nKey findings:")
    print(f"  Single CP:        {summary_1cp['map_date']}  (HDI: {summary_1cp['hdi_low']} – {summary_1cp['hdi_high']})")
    print(f"  Multi-CP dates:   {', '.join(cp_dates)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
