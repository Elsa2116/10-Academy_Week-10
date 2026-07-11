"""
data_loader.py
==============
Utilities for loading, parsing, and preprocessing the Brent oil price dataset
and the key geopolitical events CSV.
"""

import pandas as pd
import numpy as np
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data"


def load_brent_prices(filepath: str | Path = None) -> pd.DataFrame:
    """
    Load and preprocess the Brent oil price CSV.

    Parameters
    ----------
    filepath : str or Path, optional
        Path to the CSV file. Defaults to data/brent_oil_prices.csv.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
            - Date  (datetime64[ns], index)
            - Price (float64)
            - LogReturn (float64)
            - RollingStd30 (float64)
    """
    if filepath is None:
        filepath = DATA_DIR / "brent_oil_prices.csv"

    df = pd.read_csv(filepath)

    # Normalise column names
    df.columns = [c.strip() for c in df.columns]
    if "Date" not in df.columns or "Price" not in df.columns:
        raise ValueError("CSV must contain 'Date' and 'Price' columns.")

    # Parse dates  – the raw format is 'day-Mon-YY' e.g. '20-May-87'
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%b-%y")
    df = df.sort_values("Date").reset_index(drop=True)
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    df = df.dropna(subset=["Price"])

    # Derived columns
    df["LogReturn"] = np.log(df["Price"]).diff()
    df["RollingStd30"] = df["LogReturn"].rolling(window=30, min_periods=5).std()

    df = df.set_index("Date")
    return df


def load_key_events(filepath: str | Path = None) -> pd.DataFrame:
    """
    Load the compiled key geopolitical/economic events CSV.

    Returns
    -------
    pd.DataFrame
        Columns: EventDate, EventName, Category, Description
    """
    if filepath is None:
        filepath = DATA_DIR / "key_events.csv"

    df = pd.read_csv(filepath)
    df["EventDate"] = pd.to_datetime(df["EventDate"], format="%Y-%m-%d")
    df = df.sort_values("EventDate").reset_index(drop=True)
    return df


def compute_log_returns(prices: pd.Series) -> pd.Series:
    """Return log returns for a price series."""
    return np.log(prices).diff().dropna()


def get_time_index(df: pd.DataFrame) -> np.ndarray:
    """
    Return an integer time index array (0, 1, 2, …, N-1) for use in PyMC models.
    """
    return np.arange(len(df))


def split_around_event(
    df: pd.DataFrame,
    event_date: str | pd.Timestamp,
    window_days: int = 180,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Return (before, after) DataFrames centred on an event date.

    Parameters
    ----------
    df          : Full price DataFrame with DatetimeIndex.
    event_date  : The event date (string or Timestamp).
    window_days : Number of days on each side of the event.
    """
    event_date = pd.Timestamp(event_date)
    before = df.loc[event_date - pd.Timedelta(days=window_days) : event_date]
    after = df.loc[event_date : event_date + pd.Timedelta(days=window_days)]
    return before, after


def summarise_period(series: pd.Series) -> dict:
    """Return basic descriptive statistics for a price series."""
    return {
        "mean": round(float(series.mean()), 2),
        "median": round(float(series.median()), 2),
        "std": round(float(series.std()), 2),
        "min": round(float(series.min()), 2),
        "max": round(float(series.max()), 2),
        "n_obs": len(series),
    }
