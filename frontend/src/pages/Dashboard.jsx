import React, { useState } from 'react';
import SummaryCards from '../components/SummaryCards';
import PriceChart from '../components/PriceChart';
import VolatilityChart from '../components/VolatilityChart';
import DateRangeFilter from '../components/DateRangeFilter';
import { usePrices, useSummary, useChangePoints, useEvents, useVolatility } from '../hooks/useApi';

const card = { background: '#fff', borderRadius: 12, padding: '20px 24px', boxShadow: '0 2px 12px rgba(0,0,0,0.07)', marginBottom: 24 };
const sectionTitle = { fontSize: 16, fontWeight: 700, color: '#1a237e', marginBottom: 4 };
const sectionSub = { fontSize: 12, color: '#888', marginBottom: 16 };

export default function Dashboard() {
  const [start, setStart] = useState('1987-01-01');
  const [end, setEnd] = useState('2022-09-30');
  const [showEvents, setShowEvents] = useState(false);
  const [showChangePoints, setShowChangePoints] = useState(true);

  const { data: summary, loading: loadingSummary } = useSummary();
  const { data: prices, loading: loadingPrices } = usePrices(start, end);
  const { data: changePoints } = useChangePoints();
  const { data: events } = useEvents();
  const { data: volatility, loading: loadingVol } = useVolatility(start, end);

  const handleReset = () => { setStart('1987-01-01'); setEnd('2022-09-30'); };

  return (
    <div style={{ padding: '24px 28px', maxWidth: 1400, margin: '0 auto' }}>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 24, fontWeight: 800, color: '#1a237e', margin: 0 }}>Brent Oil Price Dashboard</h1>
        <p style={{ color: '#666', marginTop: 6, fontSize: 14 }}>
          Historical Brent crude oil prices (May 1987 – Sep 2022) with Bayesian change point detection.
        </p>
      </div>

      {/* Summary cards */}
      <SummaryCards summary={summary?.recent_year ? summary : null} loading={loadingSummary} />

      {/* Date range filter */}
      <div style={card}>
        <div style={sectionTitle}>Price History</div>
        <div style={sectionSub}>Brent crude oil daily closing prices (USD/barrel)</div>
        <DateRangeFilter start={start} end={end} onStartChange={setStart} onEndChange={setEnd} onReset={handleReset} />
        <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', fontSize: 13 }}>
            <input type="checkbox" checked={showChangePoints} onChange={(e) => setShowChangePoints(e.target.checked)} />
            Show change points
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', fontSize: 13 }}>
            <input type="checkbox" checked={showEvents} onChange={(e) => setShowEvents(e.target.checked)} />
            Show key events
          </label>
        </div>
        {loadingPrices ? (
          <div style={{ padding: 60, textAlign: 'center', color: '#999' }}>Loading price data…</div>
        ) : (
          <PriceChart
            prices={prices?.data}
            changePoints={changePoints?.data}
            events={events?.data}
            showEvents={showEvents}
            showChangePoints={showChangePoints}
          />
        )}
      </div>

      {/* Volatility chart */}
      <div style={card}>
        <div style={sectionTitle}>Market Volatility</div>
        <div style={sectionSub}>30-day rolling standard deviation of log returns — periods of high uncertainty</div>
        {loadingVol ? <div style={{ padding: 40, textAlign: 'center', color: '#999' }}>Loading…</div> : <VolatilityChart volatility={volatility} />}
      </div>
    </div>
  );
}
