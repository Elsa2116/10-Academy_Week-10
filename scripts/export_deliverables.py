"""
export_deliverables.py
======================
Generate the lightweight deliverable artifacts for the Birhan Energies
challenge without requiring a full Bayesian sampling run.

This script exports:
  - outputs/results.json
  - outputs/change_points.csv
  - outputs/key_events.csv
  - outputs/deliverable_summary.md

The exported artifacts are derived from the checked-in data and the API's
precomputed change point results so the project remains reproducible in
restricted environments.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import load_brent_prices, load_key_events, summarise_period


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export challenge deliverables")
    parser.add_argument("--data", default="data/brent_oil_prices.csv", help="Path to Brent price CSV")
    parser.add_argument("--events", default="data/key_events.csv", help="Path to key events CSV")
    parser.add_argument("--output", default="outputs/", help="Output directory")
    return parser.parse_args()


def build_summary(prices: pd.DataFrame, events: pd.DataFrame) -> dict:
    change_points = load_change_points()
    change_points_df = pd.DataFrame(change_points)
    return {
        "metadata": {
            "n_observations": len(prices),
            "date_range": [str(prices.index.min().date()), str(prices.index.max().date())],
            "n_events": len(events),
            "n_change_points": len(change_points_df),
        },
        "overall_stats": summarise_period(prices["Price"]),
        "change_points": change_points,
        "event_categories": events["Category"].value_counts().sort_index().to_dict(),
    }


def load_change_points() -> list[dict]:
    routes_path = Path(__file__).resolve().parent.parent / "backend" / "api" / "routes.py"
    source = routes_path.read_text(encoding="utf-8")
    module = ast.parse(source)

    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "CHANGE_POINTS":
                    return ast.literal_eval(node.value)

    raise RuntimeError("CHANGE_POINTS not found in backend/api/routes.py")


def build_markdown(summary: dict) -> str:
    metadata = summary["metadata"]
    stats = summary["overall_stats"]
    lines = [
        "# Birhan Energies Deliverable Summary",
        "",
        "## Snapshot",
        f"- Date range: {metadata['date_range'][0]} to {metadata['date_range'][1]}",
        f"- Observations: {metadata['n_observations']}",
        f"- Key events catalogued: {metadata['n_events']}",
        f"- Detected change points: {metadata['n_change_points']}",
        "",
        "## Overall Price Statistics",
        f"- Mean price: ${stats['mean']:.2f}",
        f"- Median price: ${stats['median']:.2f}",
        f"- Standard deviation: ${stats['std']:.2f}",
        f"- Minimum price: ${stats['min']:.2f}",
        f"- Maximum price: ${stats['max']:.2f}",
        "",
        "## Notes",
        "- Change points are the precomputed model outputs exposed by the Flask API.",
        "- The full Bayesian sampling workflow remains available in the notebook and CLI runner.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    prices = load_brent_prices(args.data)
    events = load_key_events(args.events)

    summary = build_summary(prices, events)
    change_points = summary["change_points"]

    (out_dir / "results.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    pd.DataFrame(change_points).to_csv(out_dir / "change_points.csv", index=False)
    events.to_csv(out_dir / "key_events.csv", index=False)
    (out_dir / "deliverable_summary.md").write_text(build_markdown(summary), encoding="utf-8")

    print(f"Exported deliverables to {out_dir.resolve()}")


if __name__ == "__main__":
    main()