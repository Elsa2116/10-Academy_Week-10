import React, { useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ReferenceLine, Legend, ResponsiveContainer, Brush,
} from 'recharts';
import { formatDate } from '../utils/formatters';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{ background: '#fff', border: '1px solid #e0e0e0', borderRadius: 8, padding: '10px 14px', fontSize: 13 }}>
        <p style={{ margin: 0, fontWeight: 600, color: '#333' }}>{formatDate(label)}</p>
        <p style={{ margin: '4px 0 0', color: '#1565C0' }}>
          Price: <strong>${Number(payload[0]?.value).toFixed(2)}/bbl</strong>
        </p>
      </div>
    );
  }
  return null;
};

export default function PriceChart({ prices, changePoints, events, showEvents, showChangePoints }) {
  if (!prices || prices.length === 0) return <div style={{ padding: 40, textAlign: 'center', color: '#999' }}>No price data available</div>;

  const data = prices.map((p) => ({ date: p.Date, price: p.Price }));

  return (
    <div style={{ width: '100%', height: 380 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: '#666' }}
            tickFormatter={(d) => new Date(d).getFullYear()}
            interval="preserveStartEnd"
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#666' }}
            tickFormatter={(v) => `$${v}`}
            domain={['auto', 'auto']}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: 12 }} />

          {showChangePoints && changePoints?.map((cp) => (
            <ReferenceLine
              key={cp.id}
              x={cp.date}
              stroke="#e74c3c"
              strokeDasharray="4 2"
              strokeWidth={1.5}
              label={{ value: '', fontSize: 0 }}
            />
          ))}

          {showEvents && events?.map((ev) => (
            <ReferenceLine
              key={ev.EventDate}
              x={ev.EventDate}
              stroke="#f39c12"
              strokeDasharray="2 4"
              strokeWidth={1}
            />
          ))}

          <Line
            type="monotone"
            dataKey="price"
            stroke="#1565C0"
            strokeWidth={1.2}
            dot={false}
            name="Brent Price (USD/bbl)"
            activeDot={{ r: 4 }}
          />
          <Brush dataKey="date" height={22} stroke="#bbb" fill="#f9f9f9"
            tickFormatter={(d) => new Date(d).getFullYear()} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
