import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  Cell, ReferenceLine, ResponsiveContainer, LabelList,
} from 'recharts';
import { formatDate, formatPct } from '../utils/formatters';

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const d = payload[0].payload;
    return (
      <div style={{ background: '#fff', border: '1px solid #ddd', borderRadius: 8, padding: '12px 16px', fontSize: 12, maxWidth: 260 }}>
        <div style={{ fontWeight: 700, marginBottom: 6, color: '#222' }}>{d.label}</div>
        <div style={{ color: '#555' }}>📅 {formatDate(d.date)}</div>
        <div style={{ marginTop: 4 }}>Before: <strong>${d.mu_before?.toFixed(2)}/bbl</strong></div>
        <div>After: <strong>${d.mu_after?.toFixed(2)}/bbl</strong></div>
        <div style={{ color: d.pct_change >= 0 ? '#2ecc71' : '#e74c3c', fontWeight: 700, marginTop: 4 }}>
          {formatPct(d.pct_change)}
        </div>
        <div style={{ fontSize: 11, color: '#888', marginTop: 6 }}>{d.associated_event}</div>
      </div>
    );
  }
  return null;
};

export default function ChangePointChart({ changePoints }) {
  if (!changePoints || changePoints.length === 0) return null;

  const data = changePoints.map((cp) => ({
    ...cp,
    pct: cp.pct_change,
    shortLabel: cp.label.length > 20 ? cp.label.substring(0, 18) + '…' : cp.label,
  }));

  return (
    <div style={{ width: '100%', height: 380 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 20, right: 20, left: 0, bottom: 80 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="shortLabel"
            tick={{ fontSize: 10, fill: '#555' }}
            angle={-35}
            textAnchor="end"
            interval={0}
          />
          <YAxis
            tickFormatter={(v) => `${v > 0 ? '+' : ''}${v.toFixed(0)}%`}
            tick={{ fontSize: 11 }}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine y={0} stroke="#333" strokeWidth={1.5} />
          <Bar dataKey="pct" name="Price Change %" radius={[4, 4, 0, 0]}>
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.pct >= 0 ? '#2ecc71' : '#e74c3c'}
                fillOpacity={0.85}
              />
            ))}
            <LabelList
              dataKey="pct"
              position="top"
              formatter={(v) => `${v > 0 ? '+' : ''}${v.toFixed(0)}%`}
              style={{ fontSize: 10, fill: '#333' }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
