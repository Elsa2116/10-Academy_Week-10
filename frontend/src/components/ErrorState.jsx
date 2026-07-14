/**
 * ErrorState.jsx
 * Reusable error display component shown when an API call fails.
 * Props:
 *   message  (string) – human-readable error text
 *   onRetry  (func)   – callback to re-fetch (shows Retry button when provided)
 *   compact  (bool)   – smaller inline variant for card sections
 */
import React from 'react';

const styles = {
  wrapper: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '40px 24px',
    textAlign: 'center',
    gap: 12,
  },
  wrapperCompact: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    padding: '12px 16px',
    background: '#fff3cd',
    border: '1px solid #ffc107',
    borderRadius: 8,
    fontSize: 13,
    color: '#856404',
  },
  icon: {
    fontSize: 32,
    lineHeight: 1,
  },
  heading: {
    fontSize: 15,
    fontWeight: 700,
    color: '#c62828',
    margin: 0,
  },
  message: {
    fontSize: 13,
    color: '#666',
    maxWidth: 360,
    lineHeight: 1.5,
    margin: 0,
  },
  retryBtn: {
    marginTop: 4,
    padding: '8px 20px',
    background: '#1a237e',
    color: '#fff',
    border: 'none',
    borderRadius: 6,
    fontSize: 13,
    fontWeight: 600,
    cursor: 'pointer',
  },
};

export default function ErrorState({ message, onRetry, compact = false }) {
  const errorText = message || 'Unable to load data. The API may be unreachable.';

  if (compact) {
    return (
      <div style={styles.wrapperCompact} role="alert">
        <span style={{ fontSize: 18 }}>⚠️</span>
        <span>{errorText}</span>
        {onRetry && (
          <button onClick={onRetry} style={{ ...styles.retryBtn, marginTop: 0, padding: '4px 12px', fontSize: 12 }}>
            Retry
          </button>
        )}
      </div>
    );
  }

  return (
    <div style={styles.wrapper} role="alert">
      <div style={styles.icon}>⚠️</div>
      <p style={styles.heading}>Failed to load data</p>
      <p style={styles.message}>{errorText}</p>
      {onRetry && (
        <button onClick={onRetry} style={styles.retryBtn}>
          Retry
        </button>
      )}
    </div>
  );
}
