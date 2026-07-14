import React from 'react';
import ChangePointChart from '../components/ChangePointChart';
import ErrorState from '../components/ErrorState';
import LoadingState from '../components/LoadingState';
import { useChangePoints } from '../hooks/useApi';
import { formatDate, formatPrice, formatPct, pctColor } from '../utils/formatters';

const card = { background: '#fff', borderRadius: 12, padding: '20px 24px', boxShadow: '0 2px 12px rgba(0,0,0,0.07)', marginBottom: 24 };

export default function Analysis() {
  const { data: changePoints, loading, error, refetch } = useChangePoints();

  return (
    <div style={{ padding: '24px 28px', maxWidth: 1400, margin: '0 auto' }}>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 24, fontWeight: 800, color: '#1a237e', margin: 0 }}>Change Point Analysis</h1>
        <p style={{ color: '#666', marginTop: 6, fontSize: 14 }}>
          Bayesian change point detection results — structural breaks in Brent oil prices and their associated events.
        </p>
      </div>

      {/* Methodology note */}
      <div style={{ ...card, background: 'linear-gradient(135deg,#e8eaf6,#f3f4f9)', border: '1px solid #c5cae9' }}>
        <div style={{ fontSize: 15, fontWeight: 700, color: '#1a237e', marginBottom: 8 }}>Methodology</div>
        <p style={{ fontSize: 13, color: '#333', lineHeight: 1.7, margin: 0 }}>
          Change points were detected using a <strong>Bayesian piecewise-constant mean model</strong> implemented in <strong>PyMC 5</strong>.
          The switch point τ has a discrete uniform prior over all observation dates. Means μ₁ (before) and μ₂ (after)
          have Normal(mean_price, 30) priors. MCMC sampling used the Metropolis algorithm (2,000 draws, 2,000 tuning steps,
          2 chains). Each detected break is cross-referenced with the key events dataset within a ±90-day window.
          HDI = 94% Highest Density Interval. All causal attributions are probabilistic — see the Assumptions &amp; Limitations document.
        </p>
      </div>

      {/* Impact bar chart */}
      <div style={card}>
        <div style={{ fontSize: 16, fontWeight: 700, color: '#1a237e', marginBottom: 4 }}>Price Impact per Change Point</div>
        <div style={{ fontSize: 12, color: '#888', marginBottom: 16 }}>Percentage change in posterior mean price (μ₂ − μ₁) / μ₁</div>
        {loading ? (
          <LoadingState message="Loading change point data…" height={240} />
        ) : error ? (
          <ErrorState message={error} onRetry={refetch} />
        ) : (
          <ChangePointChart changePoints={changePoints?.data} />
        )}
      </div>

      {/* Detailed table */}
      <div style={card}>
        <div style={{ fontSize: 16, fontWeight: 700, color: '#1a237e', marginBottom: 16 }}>Detected Change Points – Detail</div>
        {loading ? (
          <LoadingState message="Loading…" compact />
        ) : error ? (
          <ErrorState message={error} onRetry={refetch} compact />
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
              <thead>
                <tr style={{ background: '#f5f7fa' }}>
                  {['#', 'Label', 'MAP Date', 'Before (μ₁)', 'After (μ₂)', 'Change', 'HDI Range', 'Confidence', 'Associated Event'].map((h) => (
                    <th key={h} style={{ padding: '10px 14px', textAlign: 'left', fontWeight: 600, color: '#555', borderBottom: '2px solid #e0e0e0', whiteSpace: 'nowrap' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {changePoints?.data?.map((cp, i) => (
                  <tr key={cp.id} style={{ borderBottom: '1px solid #f0f0f0', background: i % 2 === 0 ? '#fff' : '#fafafa' }}>
                    <td style={{ padding: '10px 14px', color: '#888' }}>{cp.id}</td>
                    <td style={{ padding: '10px 14px', fontWeight: 600, color: '#222' }}>{cp.label}</td>
                    <td style={{ padding: '10px 14px', whiteSpace: 'nowrap' }}>{formatDate(cp.date)}</td>
                    <td style={{ padding: '10px 14px' }}>{formatPrice(cp.mu_before)}</td>
                    <td style={{ padding: '10px 14px' }}>{formatPrice(cp.mu_after)}</td>
                    <td style={{ padding: '10px 14px', fontWeight: 700, color: pctColor(cp.pct_change) }}>{formatPct(cp.pct_change)}</td>
                    <td style={{ padding: '10px 14px', fontSize: 11, color: '#777', whiteSpace: 'nowrap' }}>{formatDate(cp.hdi_low)} – {formatDate(cp.hdi_high)}</td>
                    <td style={{ padding: '10px 14px' }}>
                      <div style={{ background: '#e8f5e9', borderRadius: 10, height: 8, width: 80, overflow: 'hidden' }}>
                        <div style={{ background: '#2ecc71', height: '100%', width: `${(cp.confidence * 100).toFixed(0)}%`, borderRadius: 10 }} />
                      </div>
                      <div style={{ fontSize: 10, color: '#888', marginTop: 2 }}>{(cp.confidence * 100).toFixed(0)}%</div>
                    </td>
                    <td style={{ padding: '10px 14px', fontSize: 11, color: '#555', maxWidth: 240 }}>{cp.associated_event}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
