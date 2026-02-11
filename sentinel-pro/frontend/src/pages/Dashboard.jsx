import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import io from 'socket.io-client';
import HeatmapFn from '../components/Heatmap';
import TrendAnalysisChart from '../components/TrendAnalysisChart';
import PeakHourChart from '../components/PeakHourChart';
import ErrorBoundary from '../components/ErrorBoundary';

// Ensure this matches your backend URL. If simple CORS is used, strict localhost:8000 is fine.
const socket = io('http://localhost:8000');

function DashboardContent() {
    const navigate = useNavigate();
    const [metrics, setMetrics] = useState({
        people_count: 0,
        risk_level: 'LOW',
        audio_status: 'NORMAL',
        coordinates: []
    });
    const [logs, setLogs] = useState([]);
    const [peakHourData, setPeakHourData] = useState([]);
    const [trendData, setTrendData] = useState([]);
    const [heatmapData, setHeatmapData] = useState(new Array(10).fill(0).map(() => new Array(10).fill(0)));
    const [anomalyAlert, setAnomalyAlert] = useState(null);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            navigate('/login');
        }

        // Socket Listener
        socket.on('connect', () => console.log("Connected to WebSocket"));
        socket.on('state_update', (data) => {
            setMetrics(data);

            // Update Heatmap
            if (data.coordinates && data.coordinates.length > 0) {
                // Simple grid mapping 10x10
                const newGrid = new Array(10).fill(0).map(() => new Array(10).fill(0));
                data.coordinates.forEach(coord => {
                    const x = Math.floor(coord.x * 10); // 0-9
                    const y = Math.floor(coord.y * 10); // 0-9
                    if (x >= 0 && x < 10 && y >= 0 && y < 10) {
                        newGrid[y][x] += 1;
                    }
                });
                setHeatmapData(newGrid);
            }

            // Anomaly Check (Simple client-side check for MVP)
            // In real app, backend sends specific alert event
            if (data.risk_level === 'DANGER' || data.risk_level === 'WARN') {
                setAnomalyAlert(`High Density Alert! Risk: ${data.risk_level}`);
                // Auto dismiss after 5s
                setTimeout(() => setAnomalyAlert(null), 5000);
            }
        });

        // Fetch Logs Initial and interval
        fetchLogs();
        fetchAnalytics();
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
            const resLogs = await fetch('http://localhost:8000/api/dashboard/logs', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (resLogs.ok) {
                const data = await resLogs.json();
                setLogs(data);
            }

            // Also fetch trend data periodically
            const resTrend = await fetch('http://localhost:8000/api/analytics/trend?window_size=5', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (resTrend.ok) {
                const data = await resTrend.json();
                setTrendData(data);
            }

        } catch (e) {
            console.error("Failed to fetch logs/trend", e);
        }
    };

    const fetchAnalytics = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('http://localhost:8000/api/analytics/peak-hour', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                if (data.hourly_data) {
                    setPeakHourData(data.hourly_data);
                }
            }
        } catch (e) {
            console.error("Failed to fetch analytics", e);
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
                    <button onClick={() => navigate('/calibrate')} className="logout-btn" style={{ background: '#3b82f6' }}>Configure</button>
                    <button onClick={handleLogout} className="logout-btn">Logout</button>
                </div>
            </nav>

            <div className="dashboard-grid" style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
                {/* Left Col: Video & Trend */}
                <div className="left-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
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

                    <div className="card-panel" style={{ background: '#1e293b', padding: '1rem', borderRadius: '0.5rem' }}>
                        <h3 style={{ marginBottom: '1rem', color: '#94a3b8' }}>Crowd Trend Analysis (Live)</h3>
                        <TrendAnalysisChart data={trendData} />
                    </div>
                </div>

                {/* Right Col: Metrics */}
                <div className="metrics-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>

                    {/* Anomaly Alert Popup */}
                    {anomalyAlert && (
                        <div style={{
                            position: 'fixed', top: '20px', right: '20px',
                            background: '#ef4444', color: 'white', padding: '1rem',
                            borderRadius: '0.5rem', boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                            animation: 'pulse 1s infinite'
                        }}>
                            ⚠️ {anomalyAlert}
                        </div>
                    )}

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

                    <div className="metric-card" style={{ background: '#1e293b', padding: '1rem', borderRadius: '0.5rem' }}>
                        <h4 style={{ margin: '0 0 0.5rem 0', color: '#94a3b8' }}>Crowd Heatmap</h4>
                        <HeatmapFn xLabels={new Array(10).fill('')} yLabels={new Array(10).fill('')} data={heatmapData} />
                    </div>

                    <div className="metric-card" style={{ background: '#1e293b', padding: '1rem', borderRadius: '0.5rem' }}>
                        <h4 style={{ margin: '0 0 0.5rem 0', color: '#94a3b8' }}>Peak Hour Traffic</h4>
                        <PeakHourChart data={peakHourData} />
                    </div>


                    <div className="logs-panel" style={{ background: '#1e293b', padding: '1rem', borderRadius: '0.5rem', flexGrow: 1 }}>
                        <h4 style={{ margin: '0 0 0.5rem 0', color: '#94a3b8' }}>Recent Logs</h4>
                        <div style={{ maxHeight: '200px', overflowY: 'auto', fontSize: '0.875rem' }}>
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

export default function Dashboard() {
    return (
        <ErrorBoundary>
            <DashboardContent />
        </ErrorBoundary>
    );
}
