import React, { useState, useEffect } from 'react';
import './App.css';

// --- CONFIG ---
// Replace with your actual ngrok URL for mobile data access
const API_BASE = "http://localhost:8000";

const App = () => {
  const [data, setData] = useState(null);
  const [sessionId] = useState(() => {
    const saved = localStorage.getItem('sentinel_session');
    if (saved) return saved;
    const newId = 'SMS-' + Math.random().toString(36).substr(2, 9).toUpperCase();
    localStorage.setItem('sentinel_session', newId);
    return newId;
  });

  useEffect(() => {
    const fetchSync = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/public/mobile-sync`);
        const json = await res.json();
        setData(json);
      } catch (err) {
        console.error("Sync Error:", err);
      }
    };

    fetchSync();
    const interval = setInterval(fetchSync, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleSOS = async () => {
    if (!window.confirm("ARE YOU SURE? This will alert venue security!")) return;

    try {
      const res = await fetch(`${API_BASE}/api/public/sos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          details: `Emergency SOS from mobile user ${sessionId}`
        })
      });
      if (res.ok) alert("SOS SENT. Security has been notified.");
    } catch (err) {
      alert("Connection error. Seek nearest staff member!");
    }
  };

  if (!data) return <div className="loading">Initializing Safety Feed...</div>;

  return (
    <div className="mobile-container">
      <header className="header">
        <h1>Sentinel Attendee Safety</h1>
        <p style={{ fontSize: '0.8rem', opacity: 0.7 }}>Secure Session: {sessionId}</p>
      </header>

      <div className="alert-bar" style={{
        background: data.risk_level === 'NORMAL' ? '#065f46' : '#991b1b',
        padding: '0.8rem', borderRadius: '8px', textAlign: 'center'
      }}>
        <strong>SECURITY ALERT:</strong> {data.admin_alert}
      </div>

      <section className="map-section">
        <div className="map-card">
          <img
            src={`${API_BASE}${data.floor_plan_url}`}
            alt="Floor Plan"
            className="map-image"
          />
          <div style={{
            position: 'absolute', top: 10, right: 10,
            background: 'rgba(0,0,0,0.7)', padding: '4px 8px', borderRadius: '4px', fontSize: '0.7rem'
          }}>
            LIVE MAP
          </div>
        </div>
      </section>

      <section className="occupancy-section">
        <h3>Live Area Density</h3>
        {data.zones.map(z => (
          <div key={z.name} className="zone-meter">
            <div className="meter-header">
              <span>{z.name}</span>
              <span style={{ color: z.status === 'RED' ? '#ef4444' : z.status === 'YELLOW' ? '#f59e0b' : '#10b981' }}>
                {z.density_percentage}%
              </span>
            </div>
            <div className="progress-bar-bg">
              <div className="progress-bar-fill" style={{
                width: `${z.density_percentage}%`,
                background: z.status === 'RED' ? '#ef4444' : z.status === 'YELLOW' ? '#f59e0b' : '#10b981'
              }} />
            </div>
          </div>
        ))}
      </section>

      <footer className="sos-footer">
        <button className="sos-button" onClick={handleSOS}>
          🚨 TRIGGER SOS 🚨
        </button>
      </footer>
    </div>
  );
};

export default App;
