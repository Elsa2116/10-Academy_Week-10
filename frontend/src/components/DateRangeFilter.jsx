import React from 'react';

export default function DateRangeFilter({ start, end, onStartChange, onEndChange, onReset }) {
  return (
    <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap', marginBottom: 20 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <label style={{ fontSize: 13, color: '#555', fontWeight: 500 }}>From:</label>
        <input
          type="date"
          value={start}
          min="1987-05-20"
          max="2022-09-30"
          onChange={(e) => onStartChange(e.target.value)}
          style={{ padding: '7px 12px', borderRadius: 8, border: '1px solid #ddd', fontSize: 13, color: '#333' }}
        />
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <label style={{ fontSize: 13, color: '#555', fontWeight: 500 }}>To:</label>
        <input
          type="date"
          value={end}
          min="1987-05-20"
          max="2022-09-30"
          onChange={(e) => onEndChange(e.target.value)}
          style={{ padding: '7px 12px', borderRadius: 8, border: '1px solid #ddd', fontSize: 13, color: '#333' }}
        />
      </div>
      <button
        onClick={onReset}
        style={{ padding: '7px 16px', borderRadius: 8, border: '1px solid #1565C0', background: '#fff', color: '#1565C0', cursor: 'pointer', fontSize: 13, fontWeight: 500 }}
      >
        Reset
      </button>
    </div>
  );
}
