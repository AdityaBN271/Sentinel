import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

const ZoneManager = () => {
    const navigate = useNavigate();
    const [zones, setZones] = useState([]);
    const [currentPolygon, setCurrentPolygon] = useState([]);
    const [zoneName, setZoneName] = useState('');
    const [capacity, setCapacity] = useState(50);
    const containerRef = useRef(null);

    useEffect(() => {
        fetchZones();
    }, []);

    const fetchZones = async () => {
        try {
            const res = await fetch('http://localhost:8000/api/zones/', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            const data = await res.json();
            setZones(data);
        } catch (err) { console.error("Error fetching zones", err); }
    };

    const handleCanvasClick = (e) => {
        const rect = containerRef.current.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width;
        const y = (e.clientY - rect.top) / rect.height;
        setCurrentPolygon([...currentPolygon, [x, y]]);
    };

    const handleSaveZone = async () => {
        if (!zoneName || currentPolygon.length < 3) return alert("Add a name and at least 3 points");

        try {
            const res = await fetch('http://localhost:8000/api/zones/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    name: zoneName,
                    polygon_data: currentPolygon,
                    capacity: capacity
                })
            });
            if (res.ok) {
                fetchZones();
                setCurrentPolygon([]);
                setZoneName('');
            }
        } catch (err) { console.error("Error saving zone", err); }
    };

    const handleDeleteZone = async (id) => {
        await fetch(`http://localhost:8000/api/zones/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        fetchZones();
    };

    return (
        <div style={{ padding: '2rem', background: '#0f172a', minHeight: '100vh', color: 'white' }}>
            <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2rem' }}>
                    <h1>SVG Spatial Zone Manager</h1>
                    <button onClick={() => navigate('/dashboard')} style={{ background: '#334155', border: 'none', padding: '0.5rem 1rem', color: 'white', borderRadius: '4px', cursor: 'pointer' }}>Back to Dashboard</button>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
                    <div style={{ position: 'relative', border: '2px solid #334155', borderRadius: '8px', overflow: 'hidden' }} ref={containerRef} onClick={handleCanvasClick}>
                        <img src="/floor_plan.png" alt="Floor Plan" style={{ width: '100%', display: 'block' }} />
                        <svg style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none' }}>
                            {/* Saved Zones */}
                            {zones.map(z => {
                                const poly = JSON.parse(z.polygon_data);
                                return (
                                    <polygon
                                        key={z.id}
                                        points={poly.map(p => `${p[0] * 100},${p[1] * 100}`).join(' ')}
                                        style={{ fill: 'rgba(59, 130, 246, 0.3)', stroke: '#3b82f6', strokeWidth: 2 }}
                                    />
                                );
                            })}
                            {/* In-Progress Zone */}
                            {currentPolygon.length > 0 && (
                                <polyline
                                    points={currentPolygon.map(p => `${p[0] * 100},${p[1] * 100}`).join(' ')}
                                    style={{ fill: 'none', stroke: '#ef4444', strokeWidth: 2, strokeDasharray: '4' }}
                                />
                            )}
                        </svg>
                        <div style={{ position: 'absolute', top: 10, right: 10, background: 'rgba(0,0,0,0.6)', padding: '5px 10px', borderRadius: '4px', fontSize: '0.8rem' }}>
                            Click to draw edges. Connect at least 3 points.
                        </div>
                    </div>

                    <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '8px' }}>
                        <h3 style={{ marginBottom: '1.5rem' }}>Zone Settings</h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            <input
                                placeholder="Zone Name (e.g. Exit A)"
                                value={zoneName}
                                onChange={(e) => setZoneName(e.target.value)}
                                style={{ background: '#020617', border: '1px solid #334155', color: 'white', padding: '0.8rem', borderRadius: '4px' }}
                            />
                            <input
                                type="number"
                                placeholder="Capacity"
                                value={capacity}
                                onChange={(e) => setCapacity(e.target.value)}
                                style={{ background: '#020617', border: '1px solid #334155', color: 'white', padding: '0.8rem', borderRadius: '4px' }}
                            />
                            <button onClick={handleSaveZone} style={{ background: '#10b981', color: 'white', border: 'none', padding: '1rem', borderRadius: '4px', fontWeight: 'bold', cursor: 'pointer' }}>
                                Save Spatial Zone
                            </button>
                            <button onClick={() => setCurrentPolygon([])} style={{ background: 'transparent', border: '1px solid #ef4444', color: '#ef4444', padding: '0.6rem', borderRadius: '4px', cursor: 'pointer' }}>
                                Reset Current Drawing
                            </button>
                        </div>

                        <div style={{ marginTop: '2rem' }}>
                            <h4>Active Zones</h4>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '1rem' }}>
                                {zones.map(z => (
                                    <div key={z.id} style={{ display: 'flex', justifyContent: 'space-between', background: '#020617', padding: '0.5rem 1rem', borderRadius: '4px' }}>
                                        <span>{z.name} (Cap: {z.capacity})</span>
                                        <button onClick={() => handleDeleteZone(z.id)} style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer' }}>✖</button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ZoneManager;
