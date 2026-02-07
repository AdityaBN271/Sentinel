import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import io from 'socket.io-client';

// Ensure this matches your backend URL. If simple CORS is used, strict localhost:8000 is fine.
const socket = io('http://localhost:8000');

export default function Dashboard() {
    const navigate = useNavigate();
    const [metrics, setMetrics] = useState({
        people_count: 0,
        risk_level: 'LOW',
        audio_status: 'NORMAL',
    });
    const [logs, setLogs] = useState([]);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            navigate('/login');
        }

        // Socket Listener
        socket.on('connect', () => console.log("Connected to WebSocket"));
        socket.on('state_update', (data) => {
            setMetrics(data);
        });

        // Fetch Logs Initial and interval
        fetchLogs();
        const interval = setInterval(fetchLogs, 5000);

        return () => {
            socket.off('connect');
            socket.off('state_update');
            clearInterval(interval);
        };
    }, [navigate]);

    const fetchLogs = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('http://localhost:8000/api/dashboard/logs', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setLogs(data);
            }
        } catch (e) {
            console.error("Failed to fetch logs", e);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    const getRiskColor = (level) => {
        if (level === 'DANGER' || level === 'HIGH') return '#ef4444';
        if (level === 'WARN' || level === 'MEDIUM') return '#f59e0b';
        return '#22c55e';
    };

    return (
        <div className="dashboard-container">
            <nav className="dashboard-nav">
                <h2>Sentinel Pro Dashboard</h2>
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                    <span>Status: <b style={{ color: getRiskColor(metrics.risk_level) }}>{metrics.risk_level}</b></span>
                    <button onClick={handleLogout} className="logout-btn">Logout</button>
                </div>
            </nav>

            <div className="dashboard-grid" style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
                {/* Left Col: Video */}
                <div className="card-panel">
                    <h3 style={{ marginBottom: '1rem' }}>Live Surveillance Feed</h3>
                    <div className="video-container" style={{ overflow: 'hidden', borderRadius: '0.5rem', border: '1px solid #334155', background: '#000' }}>
                        <img
                            src="http://localhost:8000/api/dashboard/vision/stream"
                            alt="Live Feed"
                            style={{ width: '100%', height: 'auto', display: 'block', minHeight: '300px' }}
                        />
                    </div>
                </div>

                {/* Right Col: Metrics */}
                <div className="metrics-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <div className="metric-card" style={{ background: '#1e293b', padding: '1rem', borderRadius: '0.5rem' }}>
                        <h4 style={{ margin: '0 0 0.5rem 0', color: '#94a3b8' }}>People Count</h4>
                        <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: 0 }}>{metrics.people_count}</p>
                    </div>
                    <div className="metric-card" style={{ background: '#1e293b', padding: '1rem', borderRadius: '0.5rem' }}>
                        <h4 style={{ margin: '0 0 0.5rem 0', color: '#94a3b8' }}>Audio Status</h4>
                        <p style={{ fontSize: '1.5rem', margin: 0, fontWeight: 'bold', color: metrics.audio_status === 'PANIC' ? '#ef4444' : '#22c55e' }}>
                            {metrics.audio_status}
                        </p>
                    </div>

                    <div className="logs-panel" style={{ background: '#1e293b', padding: '1rem', borderRadius: '0.5rem', flexGrow: 1 }}>
                        <h4 style={{ margin: '0 0 0.5rem 0', color: '#94a3b8' }}>Recent Logs</h4>
                        <div style={{ maxHeight: '300px', overflowY: 'auto', fontSize: '0.875rem' }}>
                            {logs.map(log => (
                                <div key={log.id} style={{ borderBottom: '1px solid #334155', padding: '0.5rem 0' }}>
                                    <span style={{ color: '#94a3b8' }}>{new Date(log.timestamp).toLocaleTimeString()}</span> - <span style={{ color: getRiskColor(log.risk_score) }}>{log.risk_score}</span> (Count: {log.person_count})
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
