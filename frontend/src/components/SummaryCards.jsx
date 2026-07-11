import React from 'react';
import { formatPrice } from '../utils/formatters';

const card = (bg) => ({
  background: bg,
  borderRadius: 12,
  padding: '20px 24px',
  color: '#fff',
  boxShadow: '0 4px 15px rgba(0,0,0,0.12)',
  minWidth: 180,
  flex: 1,
});

const CARDS_DATA = (summary) => [
  { label: 'Latest Price', value: formatPrice(summary?.recent_year?.latest_price), sub: summary?.recent_year?.latest_date, bg: 'linear-gradient(135deg,#1565C0,#1976D2)' },
  { label: 'All-Time High', value: formatPrice(summary?.all_time?.max_price), sub: summary?.all_time?.max_price_date, bg: 'linear-gradient(135deg,#C62828,#E53935)' },
  { label: 'All-Time Low', value: formatPrice(summary?.all_time?.min_price), sub: summary?.all_time?.min_price_date, bg: 'linear-gradient(135deg,#2E7D32,#43A047)' },
  { label: 'Avg Price (All)', value: formatPrice(summary?.all_time?.mean_price), sub: 'USD/barrel', bg: 'linear-gradient(135deg,#4527A0,#5E35B1)' },
  { label: 'Change Points', value: summary?.change_points_count, sub: 'detected', bg: 'linear-gradient(135deg,#E65100,#F57C00)' },
  { label: 'Key Events', value: summary?.events_count, sub: 'catalogued', bg: 'linear-gradient(135deg,#00695C,#00897B)' },
];

export default function SummaryCards({ summary, loading }) {
  if (loading) return <div style={{ padding: 20, color: '#666' }}>Loading summary…</div>;
  if (!summary) return null;

  return (
    <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 28 }}>
      {CARDS_DATA(summary).map((c) => (
        <div key={c.label} style={card(c.bg)}>
          <div style={{ fontSize: 12, opacity: 0.85, marginBottom: 6 }}>{c.label}</div>
          <div style={{ fontSize: 26, fontWeight: 700 }}>{c.value}</div>
          <div style={{ fontSize: 11, opacity: 0.75, marginTop: 4 }}>{c.sub}</div>
        </div>
      ))}
    </div>
  );
}
