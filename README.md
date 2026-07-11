# Brent Oil Price Change Point Analysis
**Birhan Energies – Data Science Challenge (July 2026)**

A full end-to-end analysis of how geopolitical and macroeconomic events impact Brent crude oil prices, using Bayesian change point detection with PyMC.

---

## Project Overview

This project identifies and quantifies structural breaks in Brent oil price time series (May 1987 – September 2022) and associates them with key world events including OPEC policy changes, geopolitical conflicts, financial crises, and global pandemics.

---

## Project Structure

```
birhan_energies/
├── .vscode/settings.json          # Editor configuration
├── .github/workflows/
│   └── unittests.yml              # CI/CD pipeline
├── .gitignore
├── requirements.txt
├── README.md                       ← You are here
├── src/
│   ├── __init__.py
│   ├── data_loader.py             # Data loading & preprocessing
│   ├── change_point_model.py      # PyMC Bayesian model
│   └── visualization.py           # Reusable plotting utilities
├── notebooks/
│   ├── __init__.py
│   ├── README.md
│   └── 01_EDA_and_change_point_analysis.ipynb   # Main analysis
├── tests/
│   ├── __init__.py
│   ├── test_data_loader.py
│   └── test_change_point_model.py
├── scripts/
│   ├── __init__.py
│   ├── README.md
│   └── run_analysis.py            # CLI runner
├── data/
│   ├── brent_oil_prices.csv       # Raw price data
│   └── key_events.csv             # Compiled geopolitical events
├── docs/
│   ├── task1_analysis_workflow.md
│   └── assumptions_and_limitations.md
├── backend/
│   ├── app.py                     # Flask application entry point
│   └── api/
│       ├── __init__.py
│       └── routes.py              # REST API endpoints
└── frontend/
    ├── package.json
    ├── public/index.html
    └── src/
        ├── App.jsx
        ├── index.js
        ├── components/             # Reusable UI components
        ├── pages/                  # Page-level components
        ├── hooks/                  # Custom React hooks
        └── utils/                  # Helper functions
```

---

## Quick Start

### 1. Python Environment

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Jupyter Analysis

```bash
jupyter lab notebooks/01_EDA_and_change_point_analysis.ipynb
```

### 3. Flask Backend

```bash
cd backend
python app.py
# API available at http://localhost:5000
```

### 4. React Frontend

```bash
cd frontend
npm install
npm start
# Dashboard available at http://localhost:3000
```

---

## API Endpoints

| Method | Endpoint                    | Description                              |
|--------|-----------------------------|------------------------------------------|
| GET    | `/api/prices`               | Historical Brent oil prices              |
| GET    | `/api/prices?start=&end=`   | Prices filtered by date range            |
| GET    | `/api/change-points`        | Detected change points with statistics   |
| GET    | `/api/events`               | Key geopolitical/economic events         |
| GET    | `/api/summary`              | Dashboard summary statistics             |
| GET    | `/api/volatility`           | Rolling volatility metrics               |

---

## Key Findings

The Bayesian change point analysis detects **multiple structural breaks** in Brent oil prices, with the most significant associated with:

1. **Gulf War (1990–91)** – Price spike then collapse
2. **Asian Financial Crisis (1997–98)** – Demand shock, sharp drop
3. **9/11 & Iraq War buildup (2001–03)** – Volatility surge
4. **Commodity Supercycle peak (2008)** – All-time high ~$147/barrel
5. **Global Financial Crisis (2008–09)** – Largest single-year crash
6. **Arab Spring / Libya (2011)** – Supply disruption spike
7. **OPEC No-Cut Decision (2014–16)** – Price halving
8. **COVID-19 Pandemic (2020)** – Historic negative futures
9. **OPEC+ Recovery & Russia-Ukraine (2021–22)** – Rapid rebound

---

## Testing

```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## License

MIT License — Birhan Energies Data Science Challenge 2026
