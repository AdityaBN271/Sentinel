import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Calibrate() {
    const navigate = useNavigate();
    const [videoPoints, setVideoPoints] = useState([]);
    const [mapPoints, setMapPoints] = useState([]);
    const [mapImage, setMapImage] = useState(null);
    const [status, setStatus] = useState('');

    const videoRef = useRef(null);
    const mapRef = useRef(null);

    const handleVideoClick = (e) => {
        if (videoPoints.length >= 4) return;
        const rect = e.target.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width;
        const y = (e.clientY - rect.top) / rect.height;
        setVideoPoints([...videoPoints, { x, y }]);
    };

    const handleMapClick = (e) => {
        if (!mapImage || mapPoints.length >= 4) return;
        const rect = e.target.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width;
        const y = (e.clientY - rect.top) / rect.height;
        setMapPoints([...mapPoints, { x, y }]);
    };

    const handleImageUpload = (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => setMapImage(e.target.result);
            reader.readAsDataURL(file);
        }
    };

    const handleReset = () => {
        setVideoPoints([]);
        setMapPoints([]);
        setStatus('');
    };

    const handleSave = async () => {
        if (videoPoints.length !== 4 || mapPoints.length !== 4) {
            setStatus('Error: Need exactly 4 points on both images.');
            return;
        }

        try {
            const token = localStorage.getItem('token');
            const res = await fetch('http://localhost:8000/api/system/calibrate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    camera_points: videoPoints,
                    map_points: mapPoints
                })
            });

            if (res.ok) {
                setStatus('Success: Calibration saved!');
                setTimeout(() => navigate('/dashboard'), 2000);
            } else {
                const err = await res.json();
                setStatus(`Error: ${err.detail}`);
            }
        } catch (e) {
            setStatus(`Error: ${e.message}`);
        }
    };

    const renderOverlayPoints = (points, color) => {
        return points.map((p, i) => (
            <div
                key={i}
                style={{
                    position: 'absolute',
                    left: `${p.x * 100}%`,
                    top: `${p.y * 100}%`,
                    width: '12px',
                    height: '12px',
                    background: color,
                    borderRadius: '50%',
                    transform: 'translate(-50%, -50%)',
                    border: '2px solid white',
                    zIndex: 10,
                    pointerEvents: 'none'
                }}
            >
                <span style={{
                    position: 'absolute', top: '-20px', left: '0',
                    color: 'white', fontWeight: 'bold', textShadow: '0 0 2px black'
                }}>
                    {i + 1}
                </span>
            </div>
        ));
    };

    return (
        <div className="calibrate-container" style={{ padding: '2rem', color: '#e2e8f0' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2rem' }}>
                <h2>System Calibration</h2>
                <div>
                    <button
                        onClick={() => navigate('/dashboard')}
                        style={{ marginRight: '1rem', padding: '0.5rem 1rem', background: '#475569', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleSave}
                        disabled={videoPoints.length !== 4 || mapPoints.length !== 4}
                        style={{
                            padding: '0.5rem 1rem',
                            background: (videoPoints.length === 4 && mapPoints.length === 4) ? '#22c55e' : '#94a3b8',
                            color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer'
                        }}
                    >
                        Save Configuration
                    </button>
                </div>
            </div>

            {status && (
                <div style={{
                    padding: '1rem', marginBottom: '1rem', borderRadius: '4px',
                    background: status.startsWith('Error') ? '#ef4444' : '#22c55e',
                    color: 'white'
                }}>
                    {status}
                </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                {/* Camera Feed */}
                <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '8px' }}>
                    <h3 style={{ marginBottom: '1rem' }}>1. Camera 4-Point Selection ({videoPoints.length}/4)</h3>
                    <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '1rem' }}>
                        Click 4 corners of a known rectangular area on the floor (e.g., a mat, tile, or marked zone).
                        Order: Top-Left → Top-Right → Bottom-Right → Bottom-Left.
                    </p>
                    <div
                        style={{ position: 'relative', cursor: 'crosshair', border: '2px solid #334155' }}
                        onClick={handleVideoClick}
                    >
                        <img
                            ref={videoRef}
                            src="http://localhost:8000/api/dashboard/vision/stream"
                            alt="Camera Feed"
                            style={{ width: '100%', display: 'block' }}
                            crossOrigin="anonymous"
                        />
                        {renderOverlayPoints(videoPoints, '#ef4444')}
                    </div>
                </div>

                {/* Map View */}
                <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '8px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                        <h3>2. Floor Plan 4-Point Selection ({mapPoints.length}/4)</h3>
                        <input
                            type="file"
                            accept="image/*"
                            onChange={handleImageUpload}
                            style={{ fontSize: '0.8rem' }}
                        />
                    </div>
                    <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '1rem' }}>
                        Upload floor plan and click the SAME 4 points in the SAME order.
                    </p>

                    <div
                        style={{
                            position: 'relative',
                            cursor: mapImage ? 'crosshair' : 'not-allowed',
                            border: '2px solid #334155',
                            minHeight: '300px',
                            background: '#000',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}
                        onClick={handleMapClick}
                    >
                        {mapImage ? (
                            <img
                                ref={mapRef}
                                src={mapImage}
                                alt="Floor Plan"
                                style={{ width: '100%', display: 'block' }}
                            />
                        ) : (
                            <span style={{ color: '#64748b' }}>Upload a Map Image</span>
                        )}
                        {renderOverlayPoints(mapPoints, '#3b82f6')}
                    </div>
                </div>
            </div>

            <div style={{ marginTop: '1rem', textAlign: 'center' }}>
                <button
                    onClick={handleReset}
                    style={{ padding: '0.5rem 1rem', background: '#ef4444', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                >
                    Reset Points
                </button>
            </div>
        </div>
    );
}
