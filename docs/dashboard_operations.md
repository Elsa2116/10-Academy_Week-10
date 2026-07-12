# Dashboard Operations Guide
**Birhan Energies – Brent Oil Price Change Point Dashboard**
*Last updated: 2026-07-12*

---

## Overview

The dashboard consists of two components:
- **Flask backend** (`backend/`) — REST API serving pre-computed price data, change points, and key events
- **React frontend** (`frontend/`) — Interactive visualisation dashboard consuming the API

---

## Prerequisites

| Dependency | Minimum Version | Install |
|------------|-----------------|---------|
| Python | 3.10 | `pyenv`, system package manager |
| Node.js | 18.x | `nvm` or system |
| pnpm / npm | npm ≥ 9 | bundled with Node |
| pip | ≥ 23 | `pip install --upgrade pip` |

---

## Quick Start

### 1. Python environment and backend

```bash
# From project root
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Start the Flask API
cd backend
python app.py
# API available at http://localhost:5000
```

### 2. React frontend

```bash
# In a new terminal, from project root
cd frontend
npm install
npm start
# Dashboard available at http://localhost:3000
```

### 3. Full analysis (optional, run before backend if change points need updating)

```bash
# From project root (venv active)
jupyter lab notebooks/01_EDA_and_change_point_analysis.ipynb
# Run all cells; outputs written to outputs/
```

---

## API Reference

All endpoints are prefixed `/api`. The backend runs on port `5000` in development.

### `GET /api/prices`

Returns the full Brent oil price time series.

**Query parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `start` | ISO date | Filter records on or after this date | `?start=2008-01-01` |
| `end` | ISO date | Filter records on or before this date | `?end=2022-09-30` |

**Response schema:**
```json
{
  "count": 8900,
  "data": [
    { "Date": "1987-05-20", "Price": 18.63, "LogReturn": null, "RollingStd30": null },
    ...
  ]
}
```

**Error responses:**

| Code | Cause | Resolution |
|------|-------|------------|
| 400 | Malformed date in query parameter | Use ISO 8601 format (YYYY-MM-DD) |
| 500 | CSV file missing or unreadable | Verify `data/brent_oil_prices.csv` exists |

---

### `GET /api/change-points`

Returns detected Bayesian change points with posterior statistics.

**Response schema:**
```json
{
  "count": 17,
  "data": [
    {
      "date": "1990-09-15",
      "tau_index": 880,
      "mean_before": 19.4,
      "mean_after": 28.1,
      "regime_shift": "upward",
      "primary_event": "Iraqi Invasion of Kuwait",
      "event_date": "1990-08-02",
      "lag_days": 44,
      "confidence": "High"
    },
    ...
  ]
}
```

**Notes:**
- `tau_index` is the 0-based index into the price series.
- `confidence` reflects the `ChangePointProximity` and `ContestedAttribution` fields in `data/key_events.csv`.

---

### `GET /api/events`

Returns all key historical events from `data/key_events.csv`.

**Query parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `category` | string | Filter by event category (e.g. `OPEC Policy`) |
| `start` | ISO date | Events on or after this date |
| `end` | ISO date | Events on or before this date |

**Response schema:**
```json
{
  "count": 25,
  "data": [
    {
      "EventDate": "1990-08-02",
      "EventName": "Iraqi Invasion of Kuwait",
      "Category": "Geopolitical Conflict",
      "Description": "...",
      "ExpectedPriceImpactDirection": "Positive (spike)",
      "UncertaintyFlag": "Low",
      "ApproximateDate": "No",
      "ContestedAttribution": "No"
    },
    ...
  ]
}
```

---

### `GET /api/summary`

Returns dashboard-level statistics.

**Response schema:**
```json
{
  "all_time": {
    "date_range": ["1987-05-20", "2022-09-30"],
    "n_observations": 8900,
    "mean_price": 54.42,
    "max_price": 147.50,
    "max_price_date": "2008-07-11",
    "min_price": 9.10,
    "min_price_date": "1998-12-10"
  },
  "recent_year": {
    "mean_price": 98.5,
    "volatility": 0.2841,
    "latest_price": 88.3,
    "latest_date": "2022-09-30"
  },
  "change_points_count": 17,
  "events_count": 25
}
```

---

### `GET /api/volatility`

Returns the rolling 30-day annualised volatility series.

**Query parameters:** `start`, `end` (same as `/api/prices`)

**Response schema:**
```json
{
  "count": 8870,
  "data": [
    { "Date": "1987-07-01", "RollingStd30": 0.0142 },
    ...
  ]
}
```

---

## Frontend Component Architecture

```
frontend/src/
├── App.jsx                        # Router; mounts all page routes
├── components/
│   ├── PriceChart.jsx             # Main Recharts line chart with event markers
│   ├── ChangePointMarker.jsx      # Vertical line + tooltip overlay for change points
│   ├── EventTable.jsx             # Filterable table of key events
│   ├── SummaryCards.jsx           # KPI cards (max price, mean, n_obs)
│   ├── VolatilityChart.jsx        # Rolling volatility chart
│   └── FilterPanel.jsx            # Date-range and category filter controls
├── pages/
│   ├── Dashboard.jsx              # Main dashboard page
│   └── EventDetail.jsx            # Individual event drill-down page
├── hooks/
│   ├── usePrices.js               # Fetches /api/prices
│   ├── useChangePoints.js         # Fetches /api/change-points
│   ├── useEvents.js               # Fetches /api/events
│   └── useSummary.js              # Fetches /api/summary
└── utils/
    ├── dateUtils.js               # ISO date parsing helpers
    └── formatters.js              # Currency / percentage formatters
```

---

## Running Tests

```bash
# All tests (from project root, venv active)
pytest tests/ -v

# Specific test modules
pytest tests/test_data_loader.py -v
pytest tests/test_change_point_model.py -v
pytest tests/test_key_events.py -v       # Dataset integrity tests
pytest tests/test_dashboard_api.py -v   # API endpoint tests

# With coverage
pytest tests/ --cov=src --cov=backend --cov-report=term-missing
```

**Expected coverage targets:**

| Module | Target |
|--------|--------|
| `src/data_loader.py` | ≥ 85% |
| `src/change_point_model.py` | ≥ 70% |
| `backend/api/routes.py` | ≥ 80% |
| `data/key_events.csv` (integrity) | 100% schema |

---

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/unittests.yml`) runs on every push:

1. Install Python dependencies from `requirements.txt`
2. Run `pytest tests/` with `--tb=short`
3. Upload coverage report as artefact

**Failing CI causes:** The most common CI failure is MCMC tests timing out. The `test_change_point_model.py` tests are smoke tests that verify model structure without sampling — they should complete in < 5 seconds.

---

## Updating the Change Point Analysis

If the underlying price data or model parameters change:

1. Re-run `notebooks/01_EDA_and_change_point_analysis.ipynb` (all cells)
2. Save updated change point estimates to `outputs/change_points.json`
3. Update `backend/api/routes.py` `CHANGE_POINTS` constant if hard-coded
4. Update `docs/change_point_event_attribution.md` with any new/shifted change points
5. Verify `data/key_events.csv` `ChangePointProximity` column is still accurate
6. Run `pytest tests/test_dashboard_api.py -v` to verify API consistency

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `ModuleNotFoundError: pymc` | venv not activated or install failed | `pip install pymc>=5.0` |
| Flask `500` on `/api/prices` | `data/brent_oil_prices.csv` not found | Ensure data file is present; check `DATA_PATH` in `backend/api/routes.py` |
| Frontend CORS error | Flask-CORS not installed or not applied | `pip install flask-cors`; check `app.py` `CORS(app)` call |
| MCMC sampling hangs in tests | Full sampling invoked accidentally | Tests should use smoke-test fixtures only, not `pm.sample()` |
| `key_events.csv` test failures | CSV schema changed or file missing | Re-run `pytest tests/test_key_events.py -v --tb=long` for details |
| React `fetch` fails in development | API running on different port | Set `REACT_APP_API_BASE=http://localhost:5000` in `frontend/.env` |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `development` | Set to `production` for deployment |
| `FLASK_PORT` | `5000` | Backend port |
| `DATA_PATH` | `../data` | Path to data directory (relative to `backend/`) |
| `REACT_APP_API_BASE` | `http://localhost:5000` | API base URL for React dev server |
