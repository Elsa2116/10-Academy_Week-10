/**
 * LoadingState.jsx
 * Reusable loading indicator shown while API data is in-flight.
 * Props:
 *   message  (string) – optional label (default "Loading…")
 *   compact  (bool)   – smaller inline variant
 *   height   (number) – wrapper min-height in px (default 120)
 */
import React from 'react';

const spin = `
@keyframes be-spin {
  0%   { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
`;

export default function LoadingState({ message = 'Loading…', compact = false, height = 120 }) {
  return (
    <>
      <style>{spin}</style>
      <div
        role="status"
        aria-label={message}
        style={{
          display: 'flex',
          flexDirection: compact ? 'row' : 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: compact ? 8 : 12,
          minHeight: compact ? 'unset' : height,
          padding: compact ? '8px 0' : '20px',
        }}
      >
        <div
          style={{
            width: compact ? 16 : 28,
            height: compact ? 16 : 28,
            border: `${compact ? 2 : 3}px solid #e3e6f0`,
            borderTop: `${compact ? 2 : 3}px solid #1a237e`,
            borderRadius: '50%',
            animation: 'be-spin 0.7s linear infinite',
            flexShrink: 0,
          }}
        />
        <span style={{ fontSize: compact ? 12 : 13, color: '#999' }}>{message}</span>
      </div>
    </>
  );
}
