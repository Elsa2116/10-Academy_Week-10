# Assumptions and Limitations
**Birhan Energies – Brent Oil Price Change Point Analysis**
*Last updated: 2026-07-12 — synced with `data/key_events.csv` v2.0*

---

## Changelog

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-11 | Initial document |
| 2.0 | 2026-07-12 | Added key events dataset provenance section (§4), explicit approximate-date registry (§5), contested-attribution registry (§6), and expanded data assumptions (A1–A4 extended). Synced with `key_events.csv` new columns. |

---

## 1. Data Assumptions

| ID | Assumption | Justification |
|----|------------|---------------|
| A1 | **Data completeness:** The provided CSV accurately records official Brent ICE daily closing prices from May 1987 to September 2022. | Sourced from EIA / Bloomberg; the Brent ICE benchmark is the global standard. |
| A2 | **Missing weekends/holidays:** Non-trading day gaps are not imputed. Analysis uses only observed trading days. | Standard practice in financial time series; imputation would introduce autocorrelation. |
| A3 | **Price currency:** All prices are in nominal USD/barrel with no inflation adjustment unless explicitly stated. | Nominal prices reflect what market participants observe and react to in real time. |
| A4 | **Log-normal price process:** Daily log returns are approximately normally distributed (thin-tailed Gaussian). | Central Limit Theorem; standard in financial econometrics. Note: tail risk (Black Swan events) is underestimated by this assumption — see L1. |
| A5 | **No structural data errors:** We assume the source dataset has no systematic recording errors, bid/ask mismatches, or data-vendor adjustments not documented in the source. | Could not be independently verified for all 8,000+ observations; spot-checked against EIA public data for selected periods. |

---

## 2. Modelling Assumptions

| ID | Assumption | Justification |
|----|------------|---------------|
| A6 | **Piecewise-constant means:** The Bayesian change point model assumes the true mean price is constant within each regime. | Simplifies inference; appropriate for identifying large structural breaks. Intra-regime trends are a known limitation (see L2). |
| A7 | **Shared variance within model variants:** The single change point model uses a common σ across both regimes. | Keeps model identifiable with two observations per regime in the worst case. The multi-segment extension relaxes this. |
| A8 | **Prior independence:** Priors on μ₁, μ₂, σ, and τ are mutually independent Normal / HalfNormal / Uniform distributions. | Standard weakly-informative prior setup for Bayesian models; avoids prior correlation introducing phantom structure. |
| A9 | **MCMC convergence criterion:** Chains are treated as converged when R̂ < 1.01 and effective sample size (ESS) > 400 for all parameters. | ArviZ community standard; verified via trace plots and rank plots. |
| A10 | **±90-day proximity rule for event attribution:** A change point is attributed to an event if the event falls within 90 calendar days of the posterior MAP estimate of τ. | Oil prices typically lead/lag fundamental news by days to weeks; 90 days is conservative enough to capture pre-pricing (e.g., military build-ups) and post-lag effects (e.g., gradual sanctions). |
| A11 | **Single dominant cause per change point:** When multiple events fall within the ±90-day window of a change point, the event most directly related to physical supply/demand is favoured as the primary attribution. | Parsimony in causal narrative. All candidates within the window are listed in `docs/change_point_event_attribution.md`; multi-cause scenarios are flagged there. |

---

## 3. Limitations

### 3.1 Critical Limitations

**L1 – Correlation vs. Causation (Critical)**

The most important limitation of this analysis is the distinction between *statistical co-occurrence in time* and *proven causal impact*.

- **What we show:** The Bayesian change point model identifies dates when the statistical properties of the price series changed significantly. We *observe* that these dates often coincide with known world events.
- **What we cannot prove:** That a specific event *caused* the price change. Prices are set by the intersection of supply and demand in global commodity markets where hundreds of simultaneous factors operate. Even if an OPEC decision precedes a detected change point by 2 days, it is impossible to fully isolate its effect from concurrent factors (currency moves, economic data releases, speculative positioning).
- **Required language:** All causal language in outputs derived from this analysis should be read as *"consistent with"* or *"plausibly associated with"*, not *"definitively caused by"*. The `UncertaintyFlag` and `ContestedAttribution` fields in `data/key_events.csv` flag where this concern is most acute.

**L2 – Piecewise-constant mean**
Real oil prices exhibit trends, cycles, and seasonality within regimes. Treating each regime as having a fixed mean underestimates intra-regime variation and may split slowly-trending periods (e.g., the 2004–2008 supercycle) into multiple spurious break points.

### 3.2 Statistical Limitations

**L3 – Discrete change point assumption**
The model assumes an abrupt instantaneous switch. In reality, structural shifts may be gradual (e.g., China's demand growth across multiple years, US shale ramp-up). Gradual transitions appear as multiple discrete change points or smeared posteriors on τ.

**L4 – Prior sensitivity**
Inference results may be sensitive to the σ = 20 hyperparameter in μ priors. A sensitivity analysis varying this across {10, 20, 40} is recommended before policy submission. Results at σ_prior = 20 are reported as default.

**L5 – Omitted variables**
The model uses only Brent price as the observed variable. No conditioning variables (USD index, global GDP, inventory levels, OPEC spare capacity) are included. Detected change points may conflate multiple simultaneous economic shocks.

### 3.3 Data Limitations

**L6 – Spot vs. futures price**
The dataset reflects near-month ICE Brent futures prices (settlement basis). Long-dated futures and physical market dynamics (storage costs, shipping rates, quality differentials) are not captured.

**L7 – Aggregation bias**
Daily closing prices mask intraday volatility, flash crashes, and market-open gaps that may be relevant for certain event analyses (e.g., the Sep 2019 Abqaiq attack intraday spike was >15% but the daily close was lower).

**L8 – Sample period truncation**
The dataset ends September 2022. Events from late 2022 onward (continued Russia-Ukraine conflict, OPEC+ voluntary cuts in 2023, US Federal Reserve rate hiking cycle) are not analysed.

### 3.4 Operational Limitations

**L9 – Computational cost**
Full MCMC sampling (`draws=2000, tune=2000`) over ~8,900 observations takes 15–45 minutes on a standard CPU. GPU acceleration or variational inference (`pm.fit()`) may be needed for production use.

**L10 – Dashboard data refresh**
The Flask backend serves static pre-computed results stored in Python module constants. Real-time price updates require a dedicated data pipeline (EIA API, Alpha Vantage) and are outside the current scope.

---

## 4. Key Events Dataset Provenance

The `data/key_events.csv` file contains 25 structured events. Each row includes the following columns:

| Column | Description |
|--------|-------------|
| `EventDate` | ISO 8601 date (YYYY-MM-DD) of the event or closest conventional proxy |
| `EventName` | Short label |
| `Category` | One of: Geopolitical Conflict, Economic Shock, OPEC Policy, Demand Shock, Sanctions/Diplomacy, Market Peak, Market Anomaly, Natural Disaster / Supply Shock |
| `Description` | 1–3 sentence factual summary |
| `ExpectedPriceImpactDirection` | Directional expectation at the time of the event |
| `UncertaintyFlag` | Low / Medium / High — reflects confidence in the date and attribution |
| `ApproximateDate` | Boolean — True if the date is a model convention, not an exact event date |
| `ContestedAttribution` | Boolean — True if primary causal attribution to this event is disputed in the literature |
| `DataProvenance` | Source reference and any caveats on date verification |
| `ChangePointProximity` | Qualitative link to model-detected change points |

**General provenance:** All event dates were cross-referenced against at least two of: Reuters historical archives, OPEC official communiqués, US DoD/State Dept records, UN Security Council resolutions, IEA Oil Market Reports, and peer-reviewed academic literature on oil price determinants.

---

## 5. Approximate Date Registry

The following events in `key_events.csv` carry `ApproximateDate = True`. Analysis users must treat these as model anchors, not confirmed event timestamps.

| EventDate | EventName | Approximation Rationale |
|-----------|-----------|------------------------|
| 1997-07-02 | Asian Financial Crisis Onset | Crisis unfolded over Jul–Oct 1997; Thai baht float (2 Jul) is the conventional start but is a single national trigger for a multi-country crisis. |
| 2004-01-01 | Chinese Demand Surge Begins | Annual boundary used by IEA to mark the breakout year; actual inflection spans 2003–2005. No single date exists. |
| 2007-01-01 | US Subprime Mortgage Market Stress | Stress built throughout 2006–Q1 2007; Jan 2007 is a model convenience anchor only. Not used as a primary change point driver. |
| 2014-06-01 | US Shale Production Peaks | EIA data shows the peak quarter is Q2 2014; no single headline date. Jun 2014 is the midpoint of the peak quarter. |
| 2021-01-01 | COVID-19 Vaccine Rollouts Begin (Mass Scale) | UK rollout began 8 Dec 2020; US and EU mass rollout scaled from Jan 2021. Jan 2021 is used as the model anchor for global mass-scale vaccination. |

---

## 6. Contested Attribution Registry

The following events carry `ContestedAttribution = True`. These events appear in the dataset because they coincide with model change points, but their causal role in driving oil prices is disputed in the academic and practitioner literature.

| EventDate | EventName | Contested Aspects | Key Counter-Arguments |
|-----------|-----------|-------------------|----------------------|
| 1997-07-02 | Asian Financial Crisis Onset | Primary cause of 1997–1998 price collapse | Concurrent OPEC over-production (Iraq under Oil-for-Food ramping up) and USD strength were co-drivers. |
| 2004-01-01 | Chinese Demand Surge Begins | Sole cause of 2004–2008 supercycle | US dollar weakening, index fund commodity inflows, and OPEC supply constraints were simultaneous contributors. |
| 2009-12-22 | OPEC Maintains 2008 Production Cuts | Sole cause of 2009–2010 recovery | G20 stimulus packages, US Federal Reserve QE1, and natural demand rebound after GFC trough are equally cited. |
| 2010-12-17 | Arab Spring Begins (Tunisia) | Direct oil price driver at this date | Oil market impact was felt in Feb–Mar 2011 when Libyan disruption materialised; Dec 2010 is a political precursor, not a supply shock. |
| 2014-06-01 | US Shale Production Peaks | The peak date as a price break trigger | The price break is more directly attributable to the Nov 2014 OPEC no-cut decision; shale is a structural backdrop, not a discrete event. |

---

## 7. Summary Risk Matrix

| ID | Type | Severity | Mitigation |
|----|------|----------|------------|
| A1–A5 | Data assumptions | Low | Spot-check against EIA; document source |
| A6–A11 | Model assumptions | Medium | Report R̂, ESS; run sensitivity analysis |
| **L1** | **Correlation vs. Causation** | **High** | Use hedged causal language; flag `ContestedAttribution` events |
| L2–L3 | Model limitations | Medium | Multi-segment model; report posterior credible intervals on τ |
| L4 | Prior sensitivity | Medium | Run sensitivity across σ_prior ∈ {10, 20, 40} |
| L5 | Omitted variables | Medium | Propose VAR / structural model extensions |
| L6–L8 | Data limitations | Low–Medium | Acknowledge in report; extend dataset if needed |
| L9–L10 | Operational | Low | Document compute requirements; plan API pipeline |
