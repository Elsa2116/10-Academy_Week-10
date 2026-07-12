"""
Unit and integration tests for backend/api/routes.py (Flask dashboard API).

These tests cover:
- Route existence and HTTP status codes
- Response schema validation
- Query parameter handling (date filtering)
- Edge cases and error handling
- Data integrity between API responses and source data
"""

import pytest
import json
import sys
from pathlib import Path
from datetime import date

# Add parent to path so we can import backend modules
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from backend.app import create_app
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False

backend_required = pytest.mark.skipif(
    not BACKEND_AVAILABLE,
    reason="Flask backend not importable – check backend/app.py and requirements.txt"
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def app():
    """Create a test Flask application."""
    if not BACKEND_AVAILABLE:
        pytest.skip("Backend not available")
    application = create_app()
    application.config["TESTING"] = True
    return application


@pytest.fixture(scope="module")
def client(app):
    """Create a test client."""
    with app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# Health / root endpoint
# ---------------------------------------------------------------------------

@backend_required
class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        response = client.get("/api/health")
        data = json.loads(response.data)
        assert isinstance(data, dict)

    def test_health_has_status_field(self, client):
        response = client.get("/api/health")
        data = json.loads(response.data)
        assert "status" in data


# ---------------------------------------------------------------------------
# /api/prices endpoint
# ---------------------------------------------------------------------------

@backend_required
class TestPricesEndpoint:
    def test_prices_returns_200(self, client):
        response = client.get("/api/prices")
        assert response.status_code == 200

    def test_prices_returns_json(self, client):
        response = client.get("/api/prices")
        data = json.loads(response.data)
        assert isinstance(data, dict)

    def test_prices_has_data_key(self, client):
        response = client.get("/api/prices")
        data = json.loads(response.data)
        assert "data" in data, "Response must contain a 'data' key"

    def test_prices_data_is_list(self, client):
        response = client.get("/api/prices")
        data = json.loads(response.data)
        assert isinstance(data["data"], list)

    def test_prices_data_not_empty(self, client):
        response = client.get("/api/prices")
        data = json.loads(response.data)
        assert len(data["data"]) > 0, "Price dataset must not be empty"

    def test_prices_record_has_required_fields(self, client):
        response = client.get("/api/prices")
        data = json.loads(response.data)
        first = data["data"][0]
        assert "Date" in first, "Each price record must have a 'Date' field"
        assert "Price" in first, "Each price record must have a 'Price' field"

    def test_prices_date_is_string(self, client):
        response = client.get("/api/prices")
        data = json.loads(response.data)
        first = data["data"][0]
        assert isinstance(first["Date"], str), "Date must be a string (ISO format)"

    def test_prices_price_is_numeric(self, client):
        response = client.get("/api/prices")
        data = json.loads(response.data)
        for record in data["data"][:10]:
            assert isinstance(record["Price"], (int, float)), (
                f"Price must be numeric, got {type(record['Price'])} for {record}"
            )

    def test_prices_filter_start_date(self, client):
        response = client.get("/api/prices?start=2020-01-01")
        assert response.status_code == 200
        data = json.loads(response.data)
        if data["data"]:
            dates = [record["Date"] for record in data["data"]]
            assert all(d >= "2020-01-01" for d in dates), (
                "All returned dates should be >= start date filter"
            )

    def test_prices_filter_end_date(self, client):
        response = client.get("/api/prices?end=2010-12-31")
        assert response.status_code == 200
        data = json.loads(response.data)
        if data["data"]:
            dates = [record["Date"] for record in data["data"]]
            assert all(d <= "2010-12-31" for d in dates), (
                "All returned dates should be <= end date filter"
            )

    def test_prices_filter_date_range(self, client):
        response = client.get("/api/prices?start=2008-01-01&end=2008-12-31")
        assert response.status_code == 200
        data = json.loads(response.data)
        if data["data"]:
            dates = [record["Date"] for record in data["data"]]
            assert all("2008-01-01" <= d <= "2008-12-31" for d in dates)

    def test_prices_invalid_date_format_returns_error_or_empty(self, client):
        response = client.get("/api/prices?start=not-a-date")
        # Should return 400 or empty data, not crash with 500
        assert response.status_code in (200, 400), (
            f"Expected 200 or 400 for invalid date, got {response.status_code}"
        )


# ---------------------------------------------------------------------------
# /api/change-points endpoint
# ---------------------------------------------------------------------------

@backend_required
class TestChangepointsEndpoint:
    def test_changepoints_returns_200(self, client):
        response = client.get("/api/change-points")
        assert response.status_code == 200

    def test_changepoints_returns_json(self, client):
        response = client.get("/api/change-points")
        data = json.loads(response.data)
        assert isinstance(data, dict)

    def test_changepoints_has_data_key(self, client):
        response = client.get("/api/change-points")
        data = json.loads(response.data)
        assert "data" in data or "change_points" in data, (
            "Response must contain 'data' or 'change_points' key"
        )

    def test_changepoints_data_is_list(self, client):
        response = client.get("/api/change-points")
        data = json.loads(response.data)
        key = "data" if "data" in data else "change_points"
        assert isinstance(data[key], list)

    def test_changepoints_record_has_date(self, client):
        response = client.get("/api/change-points")
        data = json.loads(response.data)
        key = "data" if "data" in data else "change_points"
        cp_list = data[key]
        if cp_list:
            first = cp_list[0]
            assert "date" in first or "Date" in first, (
                "Each change point record must have a date field"
            )


# ---------------------------------------------------------------------------
# /api/events endpoint
# ---------------------------------------------------------------------------

@backend_required
class TestEventsEndpoint:
    def test_events_returns_200(self, client):
        response = client.get("/api/events")
        assert response.status_code == 200

    def test_events_has_data(self, client):
        response = client.get("/api/events")
        data = json.loads(response.data)
        assert "data" in data or "events" in data

    def test_events_not_empty(self, client):
        response = client.get("/api/events")
        data = json.loads(response.data)
        key = "data" if "data" in data else "events"
        assert len(data[key]) >= 10, (
            "Events endpoint must return at least 10 events (Task 1a requirement)"
        )

    def test_events_have_required_fields(self, client):
        response = client.get("/api/events")
        data = json.loads(response.data)
        key = "data" if "data" in data else "events"
        events = data[key]
        if events:
            first = events[0]
            for field in ["EventDate", "EventName", "Category"]:
                assert field in first or field.lower() in first, (
                    f"Event record missing required field '{field}': {first}"
                )


# ---------------------------------------------------------------------------
# /api/summary endpoint
# ---------------------------------------------------------------------------

@backend_required
class TestSummaryEndpoint:
    def test_summary_returns_200(self, client):
        response = client.get("/api/summary")
        assert response.status_code == 200

    def test_summary_has_all_time_section(self, client):
        response = client.get("/api/summary")
        data = json.loads(response.data)
        assert "all_time" in data, "Summary must include 'all_time' statistics"

    def test_summary_has_recent_year_section(self, client):
        response = client.get("/api/summary")
        data = json.loads(response.data)
        assert "recent_year" in data, "Summary must include 'recent_year' statistics"

    def test_summary_all_time_max_price_is_numeric(self, client):
        response = client.get("/api/summary")
        data = json.loads(response.data)
        max_price = data["all_time"].get("max_price")
        assert isinstance(max_price, (int, float)), "max_price must be numeric"

    def test_summary_all_time_max_price_near_historical_peak(self, client):
        """Brent all-time high was ~$147.50/bbl in July 2008."""
        response = client.get("/api/summary")
        data = json.loads(response.data)
        max_price = data["all_time"].get("max_price", 0)
        assert 140 <= max_price <= 155, (
            f"Expected all-time max near $147.50, got {max_price}"
        )

    def test_summary_min_price_is_positive(self, client):
        response = client.get("/api/summary")
        data = json.loads(response.data)
        min_price = data["all_time"].get("min_price", -1)
        assert min_price > 0, f"Brent spot prices should never be negative; got {min_price}"

    def test_summary_change_points_count_positive(self, client):
        response = client.get("/api/summary")
        data = json.loads(response.data)
        count = data.get("change_points_count", -1)
        assert count > 0, "Must have at least one change point detected"


# ---------------------------------------------------------------------------
# /api/volatility endpoint
# ---------------------------------------------------------------------------

@backend_required
class TestVolatilityEndpoint:
    def test_volatility_returns_200(self, client):
        response = client.get("/api/volatility")
        assert response.status_code == 200

    def test_volatility_has_data(self, client):
        response = client.get("/api/volatility")
        data = json.loads(response.data)
        assert "data" in data

    def test_volatility_values_are_positive(self, client):
        response = client.get("/api/volatility")
        data = json.loads(response.data)
        for record in data["data"][:20]:
            vol_key = next((k for k in record if "vol" in k.lower() or "std" in k.lower()), None)
            if vol_key and record[vol_key] is not None:
                assert record[vol_key] >= 0, (
                    f"Volatility values must be non-negative, got {record[vol_key]}"
                )

    def test_volatility_filter_start_date(self, client):
        response = client.get("/api/volatility?start=2020-01-01")
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Error handling tests
# ---------------------------------------------------------------------------

@backend_required
class TestErrorHandling:
    def test_404_for_unknown_route(self, client):
        response = client.get("/api/nonexistent-endpoint-xyz")
        assert response.status_code == 404

    def test_405_for_post_on_get_only_endpoint(self, client):
        response = client.post("/api/prices", json={})
        assert response.status_code in (405, 404), (
            "POST to GET-only endpoint should return 405 Method Not Allowed"
        )

    def test_future_start_date_returns_empty_or_error(self, client):
        response = client.get("/api/prices?start=2099-01-01")
        assert response.status_code in (200, 400)
        if response.status_code == 200:
            data = json.loads(response.data)
            key = "data" if "data" in data else list(data.keys())[0]
            assert isinstance(data[key], list)


# ---------------------------------------------------------------------------
# Data consistency tests
# ---------------------------------------------------------------------------

@backend_required
class TestDataConsistency:
    def test_prices_count_matches_summary(self, client):
        prices_resp = client.get("/api/prices")
        summary_resp = client.get("/api/summary")
        prices_data = json.loads(prices_resp.data)
        summary_data = json.loads(summary_resp.data)

        prices_count = len(prices_data.get("data", []))
        summary_count = summary_data.get("all_time", {}).get("n_observations", -1)

        if prices_count > 0 and summary_count > 0:
            # Allow up to 10 observations difference (date-edge trimming)
            assert abs(prices_count - summary_count) <= 10, (
                f"Price count mismatch: /api/prices returned {prices_count} records "
                f"but /api/summary reports {summary_count} observations"
            )

    def test_events_count_matches_summary(self, client):
        events_resp = client.get("/api/events")
        summary_resp = client.get("/api/summary")
        events_data = json.loads(events_resp.data)
        summary_data = json.loads(summary_resp.data)

        key = "data" if "data" in events_data else "events"
        api_count = len(events_data.get(key, []))
        summary_count = summary_data.get("events_count", -1)

        if api_count > 0 and summary_count > 0:
            assert api_count == summary_count, (
                f"Events count mismatch: /api/events returned {api_count} "
                f"but /api/summary reports {summary_count}"
            )
