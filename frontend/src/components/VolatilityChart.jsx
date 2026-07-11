import React from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{ background: '#fff', border: '1px solid #ddd', borderRadius: 8, padding: '10px 14px', fontSize: 13 }}>
        <p style={{ margin: 0, fontWeight: 600 }}>{new Date(label).toLocaleDateString('en-GB', { year: 'numeric', month: 'short' })}</p>
        <p style={{ margin: '4px 0 0', color: '#e74c3c' }}>
          Volatility: <strong>{(payload[0]?.value * 100).toFixed(2)}%</strong>
        </p>
      </div>
    );
  }
  return null;
};

export default function VolatilityChart({ volatility }) {
  if (!volatility?.data || volatility.data.length === 0) return null;

  const data = volatility.data
    .filter((d) => d.RollingStd30 !== null)
    .map((d) => ({ date: d.Date, vol: d.RollingStd30 }));

  return (
    <div style={{ width: '100%', height: 260 }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="volGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#e74c3c" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#e74c3c" stopOpacity={0.05} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 10, fill: '#777' }}
            tickFormatter={(d) => new Date(d).getFullYear()}
            interval="preserveStartEnd"
          />
          <YAxis tick={{ fontSize: 10 }} tickFormatter={(v) => `${(v * 100).toFixed(1)}%`} />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="vol"
            stroke="#e74c3c"
            strokeWidth={1.2}
            fill="url(#volGrad)"
            dot={false}
            name="30-day Volatility"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
