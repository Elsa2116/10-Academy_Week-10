import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Analysis from './pages/Analysis';
import Events from './pages/Events';

export default function App() {
  const [page, setPage] = useState('dashboard');

  const pages = {
    dashboard: <Dashboard />,
    analysis: <Analysis />,
    events: <Events />,
  };

  return (
    <div style={{ minHeight: '100vh', background: '#f5f7fa' }}>
      <Navbar activePage={page} onNavigate={setPage} />
      <main>{pages[page] || <Dashboard />}</main>
      <footer style={{
        textAlign: 'center',
        padding: '20px',
        fontSize: 12,
        color: '#aaa',
        borderTop: '1px solid #e0e0e0',
        marginTop: 40,
        background: '#fff',
      }}>
        Birhan Energies – Brent Oil Price Change Point Analysis Dashboard © 2026
      </footer>
    </div>
  );
}
