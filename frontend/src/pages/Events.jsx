import React from 'react';
import EventsTable from '../components/EventsTable';
import ErrorState from '../components/ErrorState';
import LoadingState from '../components/LoadingState';
import { useEvents } from '../hooks/useApi';

const card = { background: '#fff', borderRadius: 12, padding: '20px 24px', boxShadow: '0 2px 12px rgba(0,0,0,0.07)', marginBottom: 24 };

export default function Events() {
  const { data: events, loading, error, refetch } = useEvents();

  return (
    <div style={{ padding: '24px 28px', maxWidth: 1400, margin: '0 auto' }}>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 24, fontWeight: 800, color: '#1a237e', margin: 0 }}>Key Events Catalogue</h1>
        <p style={{ color: '#666', marginTop: 6, fontSize: 14 }}>
          Compiled dataset of major geopolitical, economic, and policy events affecting Brent oil prices (1987–2022).
        </p>
      </div>

      <div style={{ ...card, background: 'linear-gradient(135deg,#fff8e1,#fffde7)', border: '1px solid #ffe082' }}>
        <div style={{ fontSize: 14, fontWeight: 600, color: '#e65100', marginBottom: 6 }}>⚠️ Correlation ≠ Causation</div>
        <p style={{ fontSize: 13, color: '#333', lineHeight: 1.7, margin: 0 }}>
          Events in this catalogue are associated with detected statistical change points in Brent oil prices.
          While temporal proximity supports causal hypotheses, this analysis cannot prove that any individual event
          <em>caused</em> the price change. Multiple simultaneous factors always operate in commodity markets.
          All causal language should be read as <em>"consistent with"</em> or <em>"plausibly triggered by"</em>.
        </p>
      </div>

      <div style={card}>
        {loading ? (
          <LoadingState message="Loading events catalogue…" height={200} />
        ) : error ? (
          <ErrorState message={error} onRetry={refetch} />
        ) : (
          <EventsTable events={events} loading={false} />
        )}
      </div>
    </div>
  );
}
