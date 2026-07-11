/**
 * Formatting utilities for the Brent Oil Dashboard.
 */

export const formatPrice = (value) =>
  value !== null && value !== undefined
    ? `$${Number(value).toFixed(2)}`
    : 'N/A';

export const formatPct = (value) =>
  value !== null && value !== undefined
    ? `${value > 0 ? '+' : ''}${Number(value).toFixed(1)}%`
    : 'N/A';

export const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-GB', { year: 'numeric', month: 'short', day: 'numeric' });
};

export const formatDateShort = (dateStr) => {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-GB', { year: 'numeric', month: 'short' });
};

export const pctColor = (pct) => (pct >= 0 ? '#2ecc71' : '#e74c3c');

export const categoryColor = {
  'Geopolitical Conflict': '#e74c3c',
  'Economic Shock': '#e67e22',
  'OPEC Policy': '#3498db',
  'Demand Shock': '#2ecc71',
  'Sanctions/Diplomacy': '#9b59b6',
  'Market Anomaly': '#1abc9c',
  'Market Peak': '#f1c40f',
};

export const getCategoryColor = (cat) =>
  categoryColor[cat] || '#95a5a6';
