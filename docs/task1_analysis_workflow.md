# Task 1: Analysis Workflow Document
**Birhan Energies – Brent Oil Price Change Point Analysis**  
*Data Science Challenge, July 2026*

---

## 1. Objective

The overarching goal of this analysis is to determine how major geopolitical, economic, and policy events have caused **structural breaks** in Brent crude oil prices between 1987 and 2022. We quantify these breaks using Bayesian change point detection and communicate findings to investors, policymakers, and energy companies.

---

## 2. Planned Analysis Steps

### Step 1: Data Acquisition & Preparation

| Sub-step | Action | Output |
|----------|--------|--------|
| 1a | Load `brent_oil_prices.csv` (Date, Price columns) | Clean DataFrame |
| 1b | Parse dates from `day-Mon-YY` format to `datetime64` | Proper DatetimeIndex |
| 1c | Sort chronologically, handle missing values | Complete daily series |
| 1d | Compute derived metrics: log returns, 30-day rolling volatility | Enhanced DataFrame |

**Rationale:** Financial time series require log transformation to achieve approximate stationarity. Log returns `log(Pₜ) − log(Pₜ₋₁)` are the standard representation for percentage-scale price changes and are needed for stationarity-dependent statistical tests.

---

### Step 2: Exploratory Data Analysis (EDA)

| Sub-step | Action | Output |
|----------|--------|--------|
| 2a | Plot raw price series across full 35-year horizon | Figure 1 |
| 2b | Plot log returns; observe volatility clustering | Figure 2 |
| 2c | Compute descriptive statistics per decade | Summary table |
| 2d | Augmented Dickey-Fuller (ADF) test on prices & log returns | Stationarity verdict |
| 2e | KPSS test as robustness check | Stationarity verdict |
| 2f | ACF / PACF plots | Autocorrelation structure |

**Key questions:**
- Is the price series trend-stationary, difference-stationary, or neither?
- Are log returns approximately i.i.d., or do they exhibit ARCH/GARCH effects?
- Are there visually obvious structural breaks?

---

### Step 3: Event Compilation

Compile a structured dataset of 20+ major events (stored in `data/key_events.csv`) covering:
- **Geopolitical conflicts:** Gulf War, Iraq War, Arab Spring, Libya, Russia-Ukraine
- **Economic shocks:** Asian Financial Crisis, Global Financial Crisis, COVID-19
- **OPEC/supply decisions:** 1999 cuts, 2014 no-cut, 2016 OPEC+ deal, 2020 record cut
- **Sanctions:** Iran JCPOA, US-Iran reimposed, Venezuela
- **Demand shocks:** Chinese industrialisation 2004–2008, post-COVID recovery

---

### Step 4: Bayesian Change Point Modelling (PyMC)

We implement three progressive models:

#### Model 1 – Single Change Point (Baseline)
- Prior on τ: `DiscreteUniform(0, N-1)`
- Two mean parameters μ₁, μ₂ ~ `Normal(mean(prices), 30)`
- Shared σ ~ `HalfNormal(20)`
- Likelihood: `Normal(switch(τ, μ₁, μ₂), σ)`
- Sampler: Metropolis (required for discrete τ)

#### Model 2 – Multiple Change Points (Primary)
- (K−1) continuous change point fractions sorted via `pt.sort()`
- K mean parameters, shared σ
- Sampler: NUTS (continuous parameterisation)
- Model comparison via LOO-CV (ArviZ)

#### Model 3 – Volatility Change Point (Extension)
- Models structural break in variance rather than mean
- Uses log returns as the observed variable
- Detects regime shifts in market turbulence

---

### Step 5: Inference & Diagnostics

| Check | Criterion | Tool |
|-------|-----------|------|
| Convergence | R̂ < 1.01 for all parameters | `pm.summary()`, ArviZ |
| Chain mixing | Trace plots show overlapping chains | `az.plot_trace()` |
| Effective sample size | ESS_bulk > 400 | `pm.summary()` |
| Model fit | Posterior predictive check against observed data | `pm.sample_posterior_predictive()` |

---

### Step 6: Causal Attribution & Interpretation

- Map posterior mode of τ to a calendar date.
- Cross-reference with the events CSV (within a ±90-day window).
- Quantify impact: `pct_change = (μ₂_mean − μ₁_mean) / μ₁_mean × 100%`
- Write probabilistic statements: *"There is a >95% posterior probability that a structural break occurred between [date₁] and [date₂], coinciding with [event]."*

---

### Step 7: Dashboard Development (Task 3)

- Build Flask REST API exposing historical prices, change points, and events.
- Build React frontend with Recharts visualisations.
- Features: date range filter, event highlight, drill-down.

---

### Step 8: Reporting & Communication

| Audience | Format | Channel |
|----------|--------|---------|
| Government bodies / Policymakers | Formal PDF report, executive summary | Email, printed brief |
| Investors / Finance sector | Blog post (Medium-style), interactive dashboard | Web, Slack |
| Energy company operations | Technical notebook, API documentation | GitHub, internal wiki |
| Academic / Research | Full methodology appendix with code | GitHub repository |

---

## 3. Communication Channels & Formats

| Format | Description |
|--------|-------------|
| **Interactive web dashboard** | Primary tool for exploratory stakeholder engagement |
| **PDF/Markdown report** | For formal submission to policymakers and regulators |
| **Jupyter notebook** | For technical peer review and reproducibility |
| **GitHub README & Wiki** | Continuous documentation for developers |
| **Slack channel** (#all-week10) | Internal team communication and Q&A |
| **Presentation slides** | For live briefings and tutorial sessions |

---

## 4. Tools & Technologies

| Layer | Tool |
|-------|------|
| Language | Python 3.11 |
| Data manipulation | pandas, NumPy |
| Visualisation | Matplotlib, Seaborn, ArviZ |
| Bayesian modelling | PyMC ≥5.0, PyTensor |
| Statistical tests | statsmodels (ADF, KPSS) |
| Backend API | Flask 3.0, flask-cors |
| Frontend dashboard | React 18, Recharts, Axios |
| Version control | Git / GitHub |
| CI/CD | GitHub Actions |
