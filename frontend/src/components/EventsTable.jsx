import React, { useState } from 'react';
import { formatDate, getCategoryColor } from '../utils/formatters';

const CATEGORIES = ['All', 'Geopolitical Conflict', 'Economic Shock', 'OPEC Policy', 'Demand Shock', 'Sanctions/Diplomacy', 'Market Anomaly', 'Market Peak'];

export default function EventsTable({ events, loading }) {
  const [selectedCat, setSelectedCat] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');

  if (loading) return <div style={{ padding: 20, color: '#666' }}>Loading events…</div>;
  if (!events?.data) return null;

  const filtered = events.data.filter((e) => {
    const catMatch = selectedCat === 'All' || e.Category === selectedCat;
    const searchMatch = !searchTerm || e.EventName.toLowerCase().includes(searchTerm.toLowerCase()) || e.Description?.toLowerCase().includes(searchTerm.toLowerCase());
    return catMatch && searchMatch;
  });

  return (
    <div>
      {/* Filters */}
      <div style={{ display: 'flex', gap: 10, marginBottom: 16, flexWrap: 'wrap', alignItems: 'center' }}>
        <input
          placeholder="Search events…"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{ padding: '8px 14px', borderRadius: 8, border: '1px solid #ddd', fontSize: 13, width: 220 }}
        />
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCat(cat)}
              style={{
                padding: '6px 12px',
                borderRadius: 20,
                border: `2px solid ${cat === 'All' ? '#1565C0' : getCategoryColor(cat)}`,
                background: selectedCat === cat ? (cat === 'All' ? '#1565C0' : getCategoryColor(cat)) : '#fff',
                color: selectedCat === cat ? '#fff' : '#333',
                cursor: 'pointer',
                fontSize: 11,
                fontWeight: 500,
              }}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr style={{ background: '#f5f7fa' }}>
              {['Date', 'Event', 'Category', 'Expected Effect', 'Description'].map((h) => (
                <th key={h} style={{ padding: '10px 14px', textAlign: 'left', fontWeight: 600, color: '#555', borderBottom: '2px solid #e0e0e0', whiteSpace: 'nowrap' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((ev, i) => (
              <tr key={i} style={{ borderBottom: '1px solid #f0f0f0', background: i % 2 === 0 ? '#fff' : '#fafafa' }}>
                <td style={{ padding: '10px 14px', whiteSpace: 'nowrap', color: '#555' }}>{formatDate(ev.EventDate)}</td>
                <td style={{ padding: '10px 14px', fontWeight: 600, color: '#222' }}>{ev.EventName}</td>
                <td style={{ padding: '10px 14px' }}>
                  <span style={{ background: getCategoryColor(ev.Category), color: '#fff', borderRadius: 12, padding: '2px 10px', fontSize: 11 }}>
                    {ev.Category}
                  </span>
                </td>
                <td style={{ padding: '10px 14px', color: ev.ExpectedPriceEffect?.includes('Negative') ? '#e74c3c' : ev.ExpectedPriceEffect?.includes('Positive') ? '#2ecc71' : '#888', fontWeight: 500, whiteSpace: 'nowrap' }}>
                  {ev.ExpectedPriceEffect}
                </td>
                <td style={{ padding: '10px 14px', color: '#555', maxWidth: 340 }}>{ev.Description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div style={{ marginTop: 10, fontSize: 12, color: '#888' }}>{filtered.length} of {events.data.length} events shown</div>
    </div>
  );
}
