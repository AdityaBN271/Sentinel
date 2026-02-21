import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import io from 'socket.io-client';
import HeatmapFn from '../components/Heatmap';
import TrendAnalysisChart from '../components/TrendAnalysisChart';
import PeakHourChart from '../components/PeakHourChart';
import ErrorBoundary from '../components/ErrorBoundary';
import PerformancePulse from '../components/PerformancePulse';
import TacticalHeatmap from '../components/TacticalHeatmap';

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
    const [mapHeatmapData, setMapHeatmapData] = useState(new Array(10).fill(0).map(() => new Array(10).fill(0)));
    const [historicalDetections, setHistoricalDetections] = useState([]);
    const [anomalyAlert, setAnomalyAlert] = useState(null);
    const [viewMode, setViewMode] = useState('camera'); // 'camera' or 'map'

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            navigate('/login');
        }

        // Socket Listener
        socket.on('connect', () => console.log("Connected to WebSocket"));
        socket.on('state_update', (data) => {
            setMetrics(data);

            // Update Camera Heatmap
            const newCameraGrid = new Array(10).fill(0).map(() => new Array(10).fill(0));
            // Update Map Heatmap
            const newMapGrid = new Array(10).fill(0).map(() => new Array(10).fill(0));

            data.coordinates.forEach(coord => {
                // Camera Grid Mapping
                const cx = Math.floor(coord.x * 10);
                const cy = Math.floor(coord.y * 10);
                if (cx >= 0 && cx < 10 && cy >= 0 && cy < 10) {
                    newCameraGrid[cy][cx] += 1;
                }

                // Map Grid Mapping (if available)
                if (coord.map_x !== undefined && coord.map_y !== undefined) {
                    const mx = Math.floor(coord.map_x * 10);
                    const my = Math.floor(coord.map_y * 10);
                    if (mx >= 0 && mx < 10 && my >= 0 && my < 10) {
                        newMapGrid[my][mx] += 1;
                    }
                }
            });
            setHeatmapData(newCameraGrid);
            setMapHeatmapData(newMapGrid);

            // Anomaly Check (Simple client-side check for MVP)
            if (data.risk_level === 'DANGER' || data.risk_level === 'WARN') {
                setAnomalyAlert(`High Density Alert! Risk: ${data.risk_level}`);
                setTimeout(() => setAnomalyAlert(null), 5000);
            }
        });

        socket.on('config_activated', (data) => {
            console.log("Configuration Activated:", data.name);
            setAnomalyAlert(`POV Activated: ${data.name}`);
            setTimeout(() => setAnomalyAlert(null), 3000);
            fetchHistoricalHeatmap(); // Refresh heatmap with new context
        });

        // Fetch Logs Initial and interval
        const fetchHistoricalHeatmap = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/analytics/heatmap/data?limit=1000', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const data = await response.json();
                setHistoricalDetections(data);
            } catch (err) {
                console.error("Error fetching historical heatmap:", err);
            }
        };

        fetchLogs();
        fetchAnalytics();
        fetchHistoricalHeatmap();
        const interval = setInterval(() => {
            fetchLogs();
            fetchHistoricalHeatmap();
        }, 5000);

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
                    <PerformancePulse
                        fps={metrics.fps}
                        vram={metrics.vram_usage}
                        device={metrics.inference_device}
                    />
                    <span>Status: <b style={{ color: getRiskColor(metrics.risk_level) }}>{metrics.risk_level}</b></span>
                    <button onClick={() => navigate('/library')} className="logout-btn" style={{ background: '#3b82f6' }}>Library</button>
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
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                            <h4 style={{ margin: 0, color: '#94a3b8' }}>{viewMode === 'camera' ? 'Camera Heatmap' : 'Floor Plan Heatmap'}</h4>
                            <select
                                value={viewMode}
                                onChange={(e) => setViewMode(e.target.value)}
                                style={{ background: '#334155', color: 'white', border: 'none', borderRadius: '4px', fontSize: '0.75rem', padding: '0.2rem' }}
                            >
                                <option value="camera">Camera View</option>
                                <option value="map">Map View</option>
                            </select>
                        </div>
                        {viewMode === 'camera' ? (
                            <HeatmapFn xLabels={new Array(10).fill('')} yLabels={new Array(10).fill('')} data={heatmapData} />
                        ) : (
                            <TacticalHeatmap detections={historicalDetections} />
                        )}
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
