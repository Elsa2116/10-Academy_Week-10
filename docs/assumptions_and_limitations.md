# Assumptions and Limitations
**Birhan Energies – Brent Oil Price Change Point Analysis**

---

## 1. Assumptions

### 1.1 Data Assumptions
| # | Assumption | Justification |
|---|------------|---------------|
| A1 | **Data completeness:** The provided CSV accurately records official Brent ICE daily closing prices. | Sourced from EIA / Bloomberg; widely used benchmark. |
| A2 | **Missing weekends/holidays:** Non-trading day gaps are not imputed. Analysis uses only observed trading days. | Standard practice in financial time series. |
| A3 | **Price currency:** All prices are in nominal USD/barrel with no inflation adjustment unless stated. | Nominal prices are what market participants observe and react to. |
| A4 | **Log-normal price process:** Daily log returns are approximately normally distributed. | Central Limit Theorem; standard in financial econometrics. Tail risk may be underestimated. |

### 1.2 Modelling Assumptions
| # | Assumption | Justification |
|---|------------|---------------|
| A5 | **Piecewise-constant means:** The change point model assumes the true mean price is constant within each regime. | Simplifies inference; appropriate for identifying large structural breaks. |
| A6 | **Shared variance:** The single change point model uses a common σ across regimes. | Keeps model identifiable; relaxed in the volatility extension. |
| A7 | **Prior independence:** Priors on μ₁, μ₂, σ, and τ are mutually independent. | Standard weakly-informative prior setup for Bayesian models. |
| A8 | **MCMC convergence:** Chains that achieve R̂ < 1.01 and ESS > 400 are treated as converged. | ArviZ community standard; verified via trace plots. |

### 1.9 Event Attribution Assumptions
| # | Assumption | Justification |
|---|------------|---------------|
| A9 | **±90-day proximity rule:** A change point is attributed to an event if the event falls within 90 days of the posterior MAP estimate of τ. | Prices typically lead/lag fundamental news by days to weeks; 90 days is conservative. |
| A10 | **Single dominant cause:** When multiple events fall near a change point, the event most directly related to supply/demand is favoured. | Parsimony in causal narrative; multi-cause scenarios are noted in the discussion. |

---

## 2. Limitations

### 2.1 Statistical Limitations

**L1 – Correlation vs. Causation (Critical)**
The most important limitation of this analysis is the distinction between *statistical association in time* and *proven causal impact*.

- **What we show:** The Bayesian change point model identifies dates when the statistical properties of the price series changed significantly. We *observe* that these dates often coincide with known events.
- **What we cannot prove:** That a specific event *caused* the price change. Prices are set by the intersection of supply and demand in global commodity markets where **hundreds of simultaneous factors** operate. Even if an OPEC decision occurs 2 days before a detected change point, it is impossible to fully isolate its effect from concurrent factors such as currency fluctuations, economic data releases, or speculative positioning.
- **Why this matters:** Claiming causation without a valid counterfactual (e.g., a randomised experiment or a credible instrumental variable) overstates the analysis and could mislead policymakers. All causal language in this report should be read as *"consistent with"* or *"plausibly caused by"*, not *"definitively caused by"*.

**L2 – Piecewise-constant mean assumption**  
Real oil prices exhibit trends, cycles, and seasonality within regimes. Treating each regime as having a fixed mean underestimates intra-regime variation and may split slowly-trending periods into multiple spurious change points.

**L3 – Discrete change point**  
The single change point model assumes an abrupt instantaneous switch. In reality, structural shifts may be gradual (e.g., China's demand growth over several years). Gradual transitions will appear as multiple discrete change points.

**L4 – Prior sensitivity**  
Inference results may be sensitive to prior hyperparameter choices (σ = 20 for μ priors). A prior sensitivity analysis is recommended before policy submission.

**L5 – Omitted variables**  
The model uses only price as the observed variable. No conditioning variables (USD index, global GDP, inventory levels, weather) are included. Detected change points may conflate multiple economic shocks.

### 2.2 Data Limitations

**L6 – Spot vs. futures price**  
The dataset likely reflects spot or near-month futures prices. Long-dated futures and physical market dynamics (storage costs, shipping rates) are not captured.

**L7 – Aggregation bias**  
Daily closing prices mask intraday volatility, flash crashes, and market-open gaps that may be relevant for certain event analyses.

**L8 – Sample period**  
The dataset ends September 2022. Events from late 2022 onward (continued Russia-Ukraine conflict, energy crisis in Europe, Fed rate hikes) are not analysed.

### 2.3 Operational Limitations

**L9 – Computational cost**  
Full MCMC sampling with `draws=2000, tune=2000` over ~8,000 observations takes 15–45 minutes on a standard laptop CPU. GPU acceleration or variational inference (`pm.fit()`) may be needed for production use.

**L10 – Dashboard data refresh**  
The Flask backend serves static pre-computed results. Real-time streaming data integration would require a dedicated data pipeline (e.g., Alpha Vantage API, EIA API) and is out of scope.

---

## 3. Summary Table

| ID | Type | Severity | Mitigation |
|----|------|----------|------------|
| A1–A4 | Data assumptions | Low | Verify with multiple sources |
| A5–A8 | Model assumptions | Medium | Report R̂, ESS; run sensitivity analysis |
| **L1** | **Correlation vs. Causation** | **High** | Use hedged causal language throughout |
| L2–L3 | Model limitations | Medium | Use multi-segment model; report uncertainty intervals |
| L4 | Prior sensitivity | Medium | Run sensitivity analysis across prior ranges |
| L5 | Omitted variables | Medium | Note in findings; propose VAR extensions |
| L6–L8 | Data limitations | Low–Medium | Acknowledge in report; extend dataset if possible |
| L9–L10 | Operational | Low | Document compute requirements; plan API integrations |
