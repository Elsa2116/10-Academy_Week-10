"""
Unit tests for data/key_events.csv dataset integrity.

These tests validate that the key events dataset meets the structural and
semantic requirements for Task 1a of the Birhan Energies analysis.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

EVENTS_CSV_PATH = Path(__file__).parent.parent / "data" / "key_events.csv"

REQUIRED_COLUMNS = [
    "EventDate",
    "EventName",
    "Category",
    "Description",
    "ExpectedPriceImpactDirection",
    "UncertaintyFlag",
    "ApproximateDate",
    "ContestedAttribution",
    "DataProvenance",
    "ChangePointProximity",
]

VALID_CATEGORIES = {
    "Geopolitical Conflict",
    "Economic Shock",
    "OPEC Policy",
    "Demand Shock",
    "Sanctions/Diplomacy",
    "Market Peak",
    "Market Anomaly",
    "Natural Disaster / Supply Shock",
    "Geopolitical Shock",
    "Supply Shock",
}

VALID_UNCERTAINTY_FLAGS = {"Low", "Medium", "High"}

VALID_IMPACT_DIRECTIONS = {
    "Positive (spike)",
    "Positive (recovery)",
    "Positive (sustained)",
    "Positive (floor)",
    "Positive (floor/recovery)",
    "Positive (supply reduction)",
    "Positive (demand recovery)",
    "Positive (spike – lagged)",
    "Negative (reversal)",
    "Negative (demand collapse)",
    "Negative (crash)",
    "Negative (collapse)",
    "Negative (supply increase)",
    "Negative (historic low)",
    "Mixed",
    "Peak",
    "Not directly linked to model CP",
}

DATA_START_DATE = pd.Timestamp("1987-05-15")  # start of Brent price series
DATA_END_DATE = pd.Timestamp("2022-09-30")    # end of Brent price series


@pytest.fixture(scope="module")
def events_df():
    """Load and parse the key events CSV."""
    assert EVENTS_CSV_PATH.exists(), (
        f"Key events file not found at {EVENTS_CSV_PATH}. "
        "This file must be committed to the repository."
    )
    df = pd.read_csv(EVENTS_CSV_PATH, parse_dates=["EventDate"])
    return df


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------

class TestSchema:
    """Validate the structure and column presence of the dataset."""

    def test_file_exists(self):
        assert EVENTS_CSV_PATH.exists(), "key_events.csv must exist in data/"

    def test_required_columns_present(self, events_df):
        missing = [c for c in REQUIRED_COLUMNS if c not in events_df.columns]
        assert not missing, f"Missing required columns: {missing}"

    def test_minimum_row_count(self, events_df):
        """Dataset must contain at least 10 events (assessment requirement)."""
        assert len(events_df) >= 10, (
            f"Dataset has only {len(events_df)} events; at least 10 are required."
        )

    def test_no_duplicate_event_names(self, events_df):
        duplicates = events_df["EventName"][events_df["EventName"].duplicated()]
        assert duplicates.empty, f"Duplicate EventName entries found: {list(duplicates)}"

    def test_no_null_required_fields(self, events_df):
        for col in ["EventDate", "EventName", "Category", "Description",
                    "ExpectedPriceImpactDirection"]:
            null_count = events_df[col].isnull().sum()
            assert null_count == 0, f"Column '{col}' has {null_count} null values"


# ---------------------------------------------------------------------------
# Date tests
# ---------------------------------------------------------------------------

class TestDates:
    """Validate event dates are plausible and parseable."""

    def test_eventdate_is_datetime(self, events_df):
        assert pd.api.types.is_datetime64_any_dtype(events_df["EventDate"]), (
            "EventDate column should parse as datetime"
        )

    def test_dates_within_analysis_period_or_close(self, events_df):
        """Dates should be within or within 5 years of the analysis window."""
        extended_start = DATA_START_DATE - pd.Timedelta(days=365 * 5)
        extended_end = DATA_END_DATE + pd.Timedelta(days=365 * 1)
        out_of_range = events_df[
            (events_df["EventDate"] < extended_start) |
            (events_df["EventDate"] > extended_end)
        ]
        assert out_of_range.empty, (
            f"Events with dates outside expected range:\n{out_of_range[['EventDate', 'EventName']]}"
        )

    def test_dates_sorted_ascending(self, events_df):
        sorted_dates = events_df["EventDate"].sort_values().reset_index(drop=True)
        assert sorted_dates.equals(events_df["EventDate"].reset_index(drop=True)), (
            "Events should be sorted in ascending date order"
        )

    def test_no_future_dates(self, events_df):
        # All events in the dataset should predate July 2026
        today = pd.Timestamp("2026-07-12")
        future = events_df[events_df["EventDate"] > today]
        assert future.empty, f"Future-dated events found:\n{future[['EventDate', 'EventName']]}"


# ---------------------------------------------------------------------------
# Category and flag tests
# ---------------------------------------------------------------------------

class TestCategoriesAndFlags:
    """Validate controlled vocabulary fields."""

    def test_category_values(self, events_df):
        invalid = events_df[~events_df["Category"].isin(VALID_CATEGORIES)]
        assert invalid.empty, (
            f"Unknown Category values:\n{invalid[['EventName', 'Category']]}\n"
            f"Valid categories: {VALID_CATEGORIES}"
        )

    def test_uncertainty_flag_values(self, events_df):
        invalid = events_df[~events_df["UncertaintyFlag"].isin(VALID_UNCERTAINTY_FLAGS)]
        assert invalid.empty, (
            f"Invalid UncertaintyFlag values:\n{invalid[['EventName', 'UncertaintyFlag']]}"
        )

    def test_approximate_date_is_boolean_like(self, events_df):
        """ApproximateDate should contain only Yes/No or True/False."""
        valid_values = {"Yes", "No", True, False, "True", "False", 1, 0}
        col_values = set(events_df["ApproximateDate"].astype(str).str.strip())
        unexpected = col_values - {"Yes", "No", "True", "False", "1", "0"}
        assert not unexpected, (
            f"Unexpected ApproximateDate values: {unexpected}. "
            "Must be Yes/No or True/False."
        )

    def test_contested_attribution_is_boolean_like(self, events_df):
        col_values = set(events_df["ContestedAttribution"].astype(str).str.strip())
        unexpected = col_values - {"Yes", "No", "True", "False", "1", "0"}
        assert not unexpected, (
            f"Unexpected ContestedAttribution values: {unexpected}. "
            "Must be Yes/No or True/False."
        )

    def test_high_uncertainty_events_have_approximate_dates_or_contested(self, events_df):
        """High UncertaintyFlag should imply ApproximateDate=Yes or ContestedAttribution=Yes."""
        high_unc = events_df[events_df["UncertaintyFlag"] == "High"].copy()
        high_unc["ApproxOrContested"] = (
            high_unc["ApproximateDate"].astype(str).isin(["Yes", "True", "1"]) |
            high_unc["ContestedAttribution"].astype(str).isin(["Yes", "True", "1"])
        )
        unacknowledged = high_unc[~high_unc["ApproxOrContested"]]
        assert unacknowledged.empty, (
            f"High-uncertainty events should have ApproximateDate=Yes or "
            f"ContestedAttribution=Yes:\n{unacknowledged[['EventName', 'UncertaintyFlag']]}"
        )


# ---------------------------------------------------------------------------
# Content quality tests
# ---------------------------------------------------------------------------

class TestContentQuality:
    """Validate description richness and provenance documentation."""

    def test_description_min_length(self, events_df):
        """Each description should be at least 30 characters."""
        short = events_df[events_df["Description"].str.len() < 30]
        assert short.empty, (
            f"Descriptions too short (< 30 chars):\n{short[['EventName', 'Description']]}"
        )

    def test_data_provenance_not_empty(self, events_df):
        empty_prov = events_df[events_df["DataProvenance"].isnull() |
                               (events_df["DataProvenance"].str.strip() == "")]
        assert empty_prov.empty, (
            f"DataProvenance must be filled for all events. Empty:\n"
            f"{empty_prov[['EventName']]}"
        )

    def test_approximate_dates_documented_in_provenance(self, events_df):
        """Approximate dates should mention their approximation in DataProvenance."""
        approx_events = events_df[
            events_df["ApproximateDate"].astype(str).isin(["Yes", "True", "1"])
        ]
        for _, row in approx_events.iterrows():
            # Provenance should contain some hedge word
            prov = str(row["DataProvenance"]).lower()
            has_hedge = any(word in prov for word in [
                "approximate", "convention", "anchor", "model", "proxy",
                "boundary", "no single", "span"
            ])
            assert has_hedge, (
                f"Event '{row['EventName']}' has ApproximateDate=Yes but "
                f"DataProvenance does not document the approximation: '{row['DataProvenance']}'"
            )

    def test_no_events_without_categories(self, events_df):
        missing_cat = events_df[events_df["Category"].isnull() |
                                (events_df["Category"].str.strip() == "")]
        assert missing_cat.empty, (
            f"Events missing Category:\n{missing_cat[['EventName']]}"
        )

    def test_impact_direction_not_empty(self, events_df):
        empty_dir = events_df[
            events_df["ExpectedPriceImpactDirection"].isnull() |
            (events_df["ExpectedPriceImpactDirection"].str.strip() == "")
        ]
        assert empty_dir.empty, (
            f"Events with empty ExpectedPriceImpactDirection:\n{empty_dir[['EventName']]}"
        )


# ---------------------------------------------------------------------------
# Coverage tests
# ---------------------------------------------------------------------------

class TestCoverage:
    """Validate that the dataset covers key historical periods and event types."""

    def test_covers_all_major_decades(self, events_df):
        """The dataset should contain events from at least four distinct decades."""
        decades = (events_df["EventDate"].dt.year // 10).unique()
        assert len(decades) >= 4, (
            f"Dataset covers only {len(decades)} decades; expected ≥ 4. "
            f"Decades present: {sorted(decades * 10)}"
        )

    def test_opec_policy_events_present(self, events_df):
        opec_events = events_df[events_df["Category"] == "OPEC Policy"]
        assert len(opec_events) >= 3, (
            f"Expected ≥ 3 OPEC Policy events, found {len(opec_events)}"
        )

    def test_geopolitical_events_present(self, events_df):
        geo_events = events_df[events_df["Category"].str.startswith("Geopolitical")]
        assert len(geo_events) >= 3, (
            f"Expected ≥ 3 Geopolitical events, found {len(geo_events)}"
        )

    def test_economic_shock_events_present(self, events_df):
        econ_events = events_df[events_df["Category"] == "Economic Shock"]
        assert len(econ_events) >= 2, (
            f"Expected ≥ 2 Economic Shock events, found {len(econ_events)}"
        )

    def test_mix_of_positive_and_negative_impacts(self, events_df):
        positive = events_df[events_df["ExpectedPriceImpactDirection"].str.startswith("Positive")]
        negative = events_df[events_df["ExpectedPriceImpactDirection"].str.startswith("Negative")]
        assert len(positive) >= 3, f"Expected ≥ 3 positive-impact events, found {len(positive)}"
        assert len(negative) >= 3, f"Expected ≥ 3 negative-impact events, found {len(negative)}"

    def test_some_events_are_contested(self, events_df):
        """At least a few events should have ContestedAttribution=Yes for intellectual honesty."""
        contested = events_df[
            events_df["ContestedAttribution"].astype(str).isin(["Yes", "True", "1"])
        ]
        assert len(contested) >= 2, (
            f"Expected ≥ 2 contested-attribution events for rigour, found {len(contested)}"
        )

    def test_some_approximate_dates_present(self, events_df):
        """Some events should have ApproximateDate=Yes, reflecting honest uncertainty."""
        approx = events_df[
            events_df["ApproximateDate"].astype(str).isin(["Yes", "True", "1"])
        ]
        assert len(approx) >= 2, (
            f"Expected ≥ 2 approximate-date events, found {len(approx)}"
        )
