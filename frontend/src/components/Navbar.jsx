import React from 'react';

const styles = {
  nav: {
    background: 'linear-gradient(135deg, #1a237e 0%, #283593 100%)',
    color: '#fff',
    padding: '0 24px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    height: 60,
    boxShadow: '0 2px 8px rgba(0,0,0,0.25)',
    position: 'sticky',
    top: 0,
    zIndex: 100,
  },
  brand: { display: 'flex', alignItems: 'center', gap: 10 },
  logo: { fontSize: 22, fontWeight: 800, letterSpacing: 1 },
  subtitle: { fontSize: 11, opacity: 0.7, marginTop: 2 },
  links: { display: 'flex', gap: 8 },
  link: (active) => ({
    color: active ? '#fff' : 'rgba(255,255,255,0.7)',
    background: active ? 'rgba(255,255,255,0.15)' : 'transparent',
    border: 'none',
    cursor: 'pointer',
    padding: '8px 16px',
    borderRadius: 6,
    fontSize: 14,
    fontWeight: active ? 600 : 400,
    transition: 'all 0.2s',
  }),
};

export default function Navbar({ activePage, onNavigate }) {
  const pages = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'analysis', label: 'Change Points' },
    { id: 'events', label: 'Events' },
  ];
  return (
    <nav style={styles.nav}>
      <div style={styles.brand}>
        <div>
          <div style={styles.logo}>⚡ Birhan Energies</div>
          <div style={styles.subtitle}>Brent Oil Price Analysis</div>
        </div>
      </div>
      <div style={styles.links}>
        {pages.map((p) => (
          <button
            key={p.id}
            style={styles.link(activePage === p.id)}
            onClick={() => onNavigate(p.id)}
          >
            {p.label}
          </button>
        ))}
      </div>
    </nav>
  );
}
