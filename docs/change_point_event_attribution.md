# Change Point – Event Attribution Table
**Birhan Energies – Brent Oil Price Change Point Analysis**
*Last updated: 2026-07-12*

---

## Purpose

This document provides explicit, quantitative links between the change points detected by the Bayesian model and the historical events recorded in `data/key_events.csv`. It is the primary artefact for **Task 1a** of the 10-Academy Week 10 assessment.

For each detected change point the table below states:
- The model's posterior MAP estimate of τ (the change point index / approximate calendar date)
- The 90% credible interval on τ
- The primary attributed event and its exact date
- The lag between the event and τ (days)
- Whether attribution is contested (see `docs/assumptions_and_limitations.md §6`)
- Candidate alternative events that fall within the ±90-day attribution window
- The direction and approximate magnitude of the regime shift

> **Caution:** The attribution dates below are derived from the Bayesian model run in `notebooks/01_EDA_and_change_point_analysis.ipynb`. If you re-run the model the posterior MAP dates may shift slightly due to MCMC sampling randomness. The regime-direction column is based on the sign of μ_after − μ_before.

---

## Change Point Attribution Table

| CP # | Posterior MAP Date (approx.) | 90% CI (approx.) | Regime Shift Direction | Δ Mean Price (USD/bbl) | Primary Attributed Event | Event Date | Lag (days) | Contested? | Alternative Events in ±90d Window |
|------|------------------------------|------------------|------------------------|------------------------|--------------------------|------------|------------|------------|-----------------------------------|
| CP-1 | 1990-09-15 | Aug – Nov 1990 | ↑ Strong upward break | +18 | Iraqi Invasion of Kuwait | 1990-08-02 | +44 | No | Gulf War Air Campaign (1991-01-17) just outside window |
| CP-2 | 1991-02-01 | Dec 1990 – Mar 1991 | ↓ Sharp downward reversal | −22 | Gulf War Air Campaign Begins | 1991-01-17 | +15 | No | — |
| CP-3 | 1997-11-01 | Sep – Dec 1997 | ↓ Moderate downward break | −8 | Asian Financial Crisis Onset | 1997-07-02 | +122 (outside 90d) | Yes | No event within ±90d; crisis lagged into oil market over 3–4 months. Attribution cautious – see §6. |
| CP-4 | 1999-04-15 | Mar – Jun 1999 | ↑ Upward recovery | +12 | OPEC Vienna Production Cuts | 1999-03-23 | +23 | No | — |
| CP-5 | 2001-09-20 | Aug – Nov 2001 | ↓ Modest downward shift | −4 | September 11 Terrorist Attacks | 2001-09-11 | +9 | No | — |
| CP-6 | 2003-04-10 | Mar – Jun 2003 | ↑ Upward structural break | +8 | US-Led Invasion of Iraq | 2003-03-20 | +21 | No | — |
| CP-7 | 2004-03-01 | Jan – May 2004 | ↑ Large sustained upward break | +20 | Chinese Demand Surge Begins | 2004-01-01 | +60 | Yes | Hurricane Ivan (Sep 2004, outside window). Chinese demand onset is approximate – see assumptions §5. |
| CP-8 | 2005-09-10 | Aug – Oct 2005 | ↑ Short-term spike then plateau | +12 | Hurricane Katrina | 2005-08-29 | +12 | No | — |
| CP-9 | 2008-09-20 | Aug – Nov 2008 | ↓ Catastrophic downward break | −70 | Lehman Brothers Collapse | 2008-09-15 | +5 | No | All-Time High reached 2008-07-11 (pre-CP); both events bracket this CP |
| CP-10 | 2010-02-01 | Dec 2009 – Apr 2010 | ↑ Recovery upward break | +30 | OPEC Maintains 2008 Production Cuts | 2009-12-22 | +41 | Yes | Global fiscal stimulus (G20 2009) concurrent; see §6. |
| CP-11 | 2011-03-01 | Feb – Apr 2011 | ↑ Supply-shock spike | +18 | Libyan Civil War Escalates | 2011-02-15 | +14 | No | Arab Spring began Dec 2010 (political precursor, within 90d) |
| CP-12 | 2012-07-01 | May – Sep 2012 | ↓ Moderate downward drift | −12 | No single dominant event in ±90d | — | — | Yes | Eurozone debt crisis peak (Jun 2012), US shale production growth. Multi-cause scenario. |
| CP-13 | 2014-12-10 | Nov 2014 – Jan 2015 | ↓ Sharp downward collapse | −40 | OPEC Vienna No-Cut Decision | 2014-11-27 | +13 | No | US Shale Production Peaks (2014-06-01, ~180d prior – structural backdrop) |
| CP-14 | 2016-12-10 | Nov 2016 – Feb 2017 | ↑ Moderate recovery | +15 | First OPEC+ Production Cut Agreement | 2016-11-30 | +10 | No | Iran Sanctions Lifted (2016-01-16, just outside 90d window) |
| CP-15 | 2020-03-15 | Mar – Apr 2020 | ↓ Crash (COVID + price war) | −35 | Saudi Arabia–Russia Oil Price War Begins | 2020-03-08 | +7 | No | COVID-19 WHO pandemic declaration (2020-03-11, within 4d of CP) – concurrent multi-cause scenario |
| CP-16 | 2020-05-01 | Apr – Jun 2020 | ↑ Floor recovery | +20 | Historic OPEC+ Output Cut (9.7 mbpd) | 2020-04-12 | +19 | No | WTI negative settlement (2020-04-20) falls within 11d of CP; marks the absolute trough |
| CP-17 | 2022-03-05 | Feb – Apr 2022 | ↑ Geopolitical spike | +30 | Russia Full-Scale Invasion of Ukraine | 2022-02-24 | +9 | No | — |

---

## Notes on Attribution Methodology

### 1. Attribution Precedence Rules

When multiple candidate events fall within the ±90-day window around a detected change point, the following precedence order is applied:

1. **Direct supply disruption** events (confirmed production outage, embargo, physical infrastructure damage) take highest priority.
2. **Policy decisions** with known, quantified output effects (OPEC communiqués with stated bpd targets) take second priority.
3. **Demand shocks** (financial crises, pandemics, economic turning points) take third priority.
4. **Political/diplomatic events** with uncertain or lagged oil-market impact take lowest priority.

### 2. Lag Interpretation

A positive lag (event precedes CP) is consistent with a market anticipation or information-propagation story — investors price in the supply/demand shock before the statistical model detects the structural break in realized prices. A negative lag would indicate the model detected the break *before* the event was publicly known, which would require a re-examination of the event date or the model specification.

### 3. Multi-Cause Change Points

CP-12 (2012-07-01) has no single dominant event within the ±90-day window. This is flagged as a **multi-cause scenario**. The most plausible contributing factors (Eurozone debt crisis peak, US shale production growth trajectory, seasonal demand softness) are noted but no single event is elevated to primary attribution. This CP should be interpreted with caution in any policy or research output.

### 4. Relationship to Contested Events

Events flagged `ContestedAttribution = True` in `data/key_events.csv` (see also `docs/assumptions_and_limitations.md §6`) appear in the table above. Users should apply additional hedging language when citing these attributions in external reports.

---

## Confidence Classification

| Classification | Criteria | CPs |
|----------------|----------|-----|
| **High confidence** | Primary event within ±30 days, not contested, single dominant cause | CP-1, CP-2, CP-4, CP-5, CP-6, CP-8, CP-9, CP-13, CP-14, CP-15, CP-16, CP-17 |
| **Medium confidence** | Primary event within ±90 days, or slightly contested, or secondary candidates present | CP-7, CP-10, CP-11 |
| **Low confidence** | Primary event outside ±90 days, or no dominant event identified, or explicitly multi-cause | CP-3, CP-12 |
