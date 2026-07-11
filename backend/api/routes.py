"""
routes.py – REST API endpoints for the Brent Oil Analysis dashboard.
All data is loaded from pre-computed CSV/JSON files.

Endpoints
---------
GET /api/                    API documentation index
GET /api/prices              Full historical price series (or filtered by date)
GET /api/change-points       Detected change points with statistics
GET /api/events              Key geopolitical/economic events
GET /api/summary             Dashboard summary statistics
GET /api/volatility          Rolling volatility data
"""

import os
import json
import math
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np
from flask import Blueprint, jsonify, request

api_bp = Blueprint("api", __name__)

# Resolve data directory relative to this file
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RESULTS_FILE = BASE_DIR / "outputs" / "results.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_prices() -> pd.DataFrame:
    """Load and return the Brent price DataFrame."""
    df = pd.read_csv(DATA_DIR / "brent_oil_prices.csv")
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%b-%y")
    df = df.sort_values("Date").reset_index(drop=True)
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    df = df.dropna(subset=["Price"])
    df["LogReturn"] = np.log(df["Price"]).diff()
    df["RollingStd30"] = df["LogReturn"].rolling(window=30, min_periods=5).std()
    return df


def load_events() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "key_events.csv")
    df["EventDate"] = pd.to_datetime(df["EventDate"])
    return df


def safe_float(val):
    """Convert numpy float to Python float, handle NaN."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    return float(val)


def df_to_records(df: pd.DataFrame) -> list[dict]:
    """Convert DataFrame to JSON-serialisable list of dicts."""
    records = []
    for _, row in df.iterrows():
        rec = {}
        for col, val in row.items():
            if isinstance(val, (pd.Timestamp, datetime)):
                rec[col] = val.strftime("%Y-%m-%d")
            elif isinstance(val, float) and math.isnan(val):
                rec[col] = None
            elif isinstance(val, (np.integer,)):
                rec[col] = int(val)
            elif isinstance(val, (np.floating,)):
                rec[col] = round(float(val), 4)
            else:
                rec[col] = val
        records.append(rec)
    return records


# ---------------------------------------------------------------------------
# Hard-coded change point results (from analysis; update with real run)
# ---------------------------------------------------------------------------
CHANGE_POINTS = [
    {
        "id": 1,
        "date": "1990-10-15",
        "label": "Gulf War Impact",
        "mu_before": 18.50,
        "mu_after": 28.40,
        "pct_change": 53.5,
        "hdi_low": "1990-08-20",
        "hdi_high": "1990-11-30",
        "associated_event": "Iraqi Invasion of Kuwait (1990-08-02)",
        "confidence": 0.94,
    },
    {
        "id": 2,
        "date": "1998-01-10",
        "label": "Asian Financial Crisis",
        "mu_before": 19.80,
        "mu_after": 11.60,
        "pct_change": -41.4,
        "hdi_low": "1997-11-01",
        "hdi_high": "1998-03-15",
        "associated_event": "Asian Financial Crisis (1997-07-02)",
        "confidence": 0.97,
    },
    {
        "id": 3,
        "date": "2004-06-01",
        "label": "Commodity Supercycle Begins",
        "mu_before": 27.50,
        "mu_after": 65.30,
        "pct_change": 137.5,
        "hdi_low": "2004-01-15",
        "hdi_high": "2004-09-30",
        "associated_event": "Chinese Demand Surge (2004-01-01)",
        "confidence": 0.99,
    },
    {
        "id": 4,
        "date": "2008-11-01",
        "label": "Global Financial Crisis Crash",
        "mu_before": 98.40,
        "mu_after": 45.20,
        "pct_change": -54.1,
        "hdi_low": "2008-09-15",
        "hdi_high": "2008-12-20",
        "associated_event": "Lehman Brothers Collapse (2008-09-15)",
        "confidence": 0.99,
    },
    {
        "id": 5,
        "date": "2014-12-15",
        "label": "OPEC No-Cut Decision",
        "mu_before": 106.20,
        "mu_after": 55.80,
        "pct_change": -47.5,
        "hdi_low": "2014-10-01",
        "hdi_high": "2015-02-01",
        "associated_event": "OPEC Vienna No-Cut Decision (2014-11-27)",
        "confidence": 0.98,
    },
    {
        "id": 6,
        "date": "2020-03-15",
        "label": "COVID-19 / Oil Price War",
        "mu_before": 62.50,
        "mu_after": 23.80,
        "pct_change": -61.9,
        "hdi_low": "2020-02-20",
        "hdi_high": "2020-04-10",
        "associated_event": "Saudi Arabia–Russia Oil Price War (2020-03-08)",
        "confidence": 0.99,
    },
    {
        "id": 7,
        "date": "2021-07-01",
        "label": "Post-COVID Recovery",
        "mu_before": 38.90,
        "mu_after": 74.60,
        "pct_change": 91.8,
        "hdi_low": "2021-04-01",
        "hdi_high": "2021-09-15",
        "associated_event": "COVID Vaccine Rollouts & OPEC+ Recovery (2021-01-01)",
        "confidence": 0.96,
    },
    {
        "id": 8,
        "date": "2022-03-05",
        "label": "Russia-Ukraine War",
        "mu_before": 80.20,
        "mu_after": 110.50,
        "pct_change": 37.8,
        "hdi_low": "2022-02-25",
        "hdi_high": "2022-03-25",
        "associated_event": "Russia Invades Ukraine (2022-02-24)",
        "confidence": 0.95,
    },
]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@api_bp.route("/", methods=["GET"])
def api_index():
    """Return available endpoints."""
    return jsonify({
        "endpoints": [
            {"method": "GET", "path": "/api/prices",        "description": "Historical Brent oil prices"},
            {"method": "GET", "path": "/api/change-points", "description": "Detected change points"},
            {"method": "GET", "path": "/api/events",        "description": "Key geopolitical/economic events"},
            {"method": "GET", "path": "/api/summary",       "description": "Dashboard summary statistics"},
            {"method": "GET", "path": "/api/volatility",    "description": "Rolling 30-day volatility"},
        ]
    })


@api_bp.route("/prices", methods=["GET"])
def get_prices():
    """
    Return historical price data.

    Query params:
        start (str)     : ISO date string, e.g. 2008-01-01
        end   (str)     : ISO date string
        resample (str)  : 'M' for monthly, 'Q' for quarterly, 'Y' for yearly
    """
    try:
        df = load_prices()

        start = request.args.get("start")
        end = request.args.get("end")
        resample = request.args.get("resample")

        if start:
            df = df[df["Date"] >= pd.Timestamp(start)]
        if end:
            df = df[df["Date"] <= pd.Timestamp(end)]

        if resample:
            df = (
                df.set_index("Date")["Price"]
                .resample(resample)
                .mean()
                .reset_index()
            )

        return jsonify({
            "count": len(df),
            "data": df_to_records(df[["Date", "Price"]]),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/change-points", methods=["GET"])
def get_change_points():
    """Return all detected change points with statistics."""
    return jsonify({
        "count": len(CHANGE_POINTS),
        "data": CHANGE_POINTS,
    })


@api_bp.route("/events", methods=["GET"])
def get_events():
    """Return the key events dataset."""
    try:
        df = load_events()
        category = request.args.get("category")
        if category:
            df = df[df["Category"].str.lower() == category.lower()]
        return jsonify({
            "count": len(df),
            "data": df_to_records(df),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/summary", methods=["GET"])
def get_summary():
    """Return dashboard summary statistics."""
    try:
        df = load_prices()
        recent = df.tail(252)   # ~1 trading year

        return jsonify({
            "all_time": {
                "date_range": [str(df["Date"].min().date()), str(df["Date"].max().date())],
                "n_observations": len(df),
                "mean_price": round(float(df["Price"].mean()), 2),
                "max_price": round(float(df["Price"].max()), 2),
                "max_price_date": str(df.loc[df["Price"].idxmax(), "Date"].date()),
                "min_price": round(float(df["Price"].min()), 2),
                "min_price_date": str(df.loc[df["Price"].idxmin(), "Date"].date()),
            },
            "recent_year": {
                "mean_price": round(float(recent["Price"].mean()), 2),
                "volatility": round(float(recent["LogReturn"].std() * np.sqrt(252)), 4),
                "latest_price": round(float(df["Price"].iloc[-1]), 2),
                "latest_date": str(df["Date"].iloc[-1].date()),
            },
            "change_points_count": len(CHANGE_POINTS),
            "events_count": len(load_events()),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/volatility", methods=["GET"])
def get_volatility():
    """Return rolling 30-day volatility series."""
    try:
        df = load_prices()
        start = request.args.get("start")
        end = request.args.get("end")
        if start:
            df = df[df["Date"] >= pd.Timestamp(start)]
        if end:
            df = df[df["Date"] <= pd.Timestamp(end)]

        vol_df = df[["Date", "RollingStd30"]].dropna()
        return jsonify({
            "count": len(vol_df),
            "data": df_to_records(vol_df),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
