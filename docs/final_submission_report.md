# Birhan Energies Final Submission Report

## Brent Oil Price Change Point Analysis

This project studies how geopolitical, economic, and OPEC policy events affect Brent crude oil prices from May 1987 to September 2022. The core workflow combines exploratory time-series analysis, Bayesian change point detection, event attribution, and an interactive dashboard for stakeholder exploration.

## Executive Summary

The analysis identifies eight major structural breaks in the Brent price series and aligns them with major market events such as the Gulf War, the Asian Financial Crisis, the 2008 Global Financial Crisis, the 2014 OPEC no-cut decision, the 2020 oil price war and COVID shock, and the 2022 Russia-Ukraine war. The largest estimated regime shifts show changes of more than 50 percent in the posterior mean price between before/after segments, which is consistent with large supply-demand shocks in the global oil market.

The project is intentionally careful about causality. The model identifies statistical change points in time; the event catalogue provides plausible explanations, but the analysis does not claim experimental proof of causation.

## Dataset and Preparation

The raw Brent dataset contains 9,228 daily observations covering 1987-05-20 to 2022-09-30. Dates are parsed into a proper datetime index, prices are coerced to numeric values, and derived features are computed for analysis:

- log returns: `log(P_t) - log(P_{t-1})`
- 30-day rolling volatility of log returns

The event catalogue contains 22 major geopolitical, macroeconomic, and policy events across the same period.

## Exploratory Findings

The raw price series shows a long-run upward drift with pronounced shock periods. Log returns provide a more stationary view and reveal volatility clustering around major world events. This supports the modelling choice of using change point methods rather than a single global mean model.

## Bayesian Change Point Modeling

The main model uses a discrete switch point prior over all valid dates and two regime means before and after the switch. The likelihood is Gaussian with a shared standard deviation. This is a standard baseline for identifying abrupt structural breaks in a noisy price series.

The implementation also includes a multi-segment extension and supporting utilities for posterior summaries and date extraction. The outputs are saved in `outputs/results.json` and `outputs/change_points.csv`.

## Key Results

The precomputed change point summary in `outputs/results.json` reports the following major shifts:

| Date       |                         Label | Before | After |  Change |
| ---------- | ----------------------------: | -----: | ----: | ------: |
| 1990-10-15 |               Gulf War Impact |   18.5 |  28.4 |  +53.5% |
| 1998-01-10 |        Asian Financial Crisis |   19.8 |  11.6 |  -41.4% |
| 2004-06-01 |   Commodity Supercycle Begins |   27.5 |  65.3 | +137.5% |
| 2008-11-01 | Global Financial Crisis Crash |   98.4 |  45.2 |  -54.1% |
| 2014-12-15 |          OPEC No-Cut Decision |  106.2 |  55.8 |  -47.5% |
| 2020-03-15 |      COVID-19 / Oil Price War |   62.5 |  23.8 |  -61.9% |
| 2021-07-01 |           Post-COVID Recovery |   38.9 |  74.6 |  +91.8% |
| 2022-03-05 |            Russia-Ukraine War |   80.2 | 110.5 |  +37.8% |

These shifts are broadly consistent with the event catalogue and the known direction of major oil-market shocks.

## Dashboard Deliverable

The React dashboard exposes the price series, change point summaries, event catalogue, summary cards, and volatility chart through a simple navigation layout. The backend API serves the precomputed analysis outputs through REST endpoints for prices, events, change points, summary statistics, and rolling volatility.

## Assumptions and Limitations

The analysis assumes nominal USD prices, no imputation of missing trading days, and a piecewise-constant regime structure within each identified segment. The most important limitation is the distinction between correlation and causation: the change point model detects statistical breaks in time, but it cannot prove that a specific event caused the change without a counterfactual design.

Other important limitations include omitted macroeconomic variables, gradual structural shifts that may appear as multiple abrupt breaks, and the computational cost of full Bayesian sampling on a large daily series.

## Deliverables Included

- `data/key_events.csv`
- `docs/task1_analysis_workflow.md`
- `docs/assumptions_and_limitations.md`
- `notebooks/01_EDA_and_change_point_analysis.ipynb`
- `outputs/results.json`
- `outputs/change_points.csv`
- `outputs/key_events.csv`
- `outputs/deliverable_summary.md`
- `outputs/fig_01_price_series.png`
- `outputs/fig_02_log_returns.png`
- `outputs/fig_03_change_points.png`
- `outputs/fig_04_event_impact.png`
- Flask backend in `backend/`
- React dashboard in `frontend/`

## Future Work

Future extensions could add macroeconomic control variables such as GDP, inflation, exchange rates, and inventories; compare the baseline model with VAR or Markov-switching alternatives; and replace the static backend with a live data pipeline.

## Conclusion

The project provides a complete end-to-end framework for identifying major Brent oil price structural breaks, interpreting them against known market events, and presenting the results through an interactive dashboard.
