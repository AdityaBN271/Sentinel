import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const ConfigurationLibrary = () => {
    const [calibrations, setCalibrations] = useState([]);
    const [selectedConfig, setSelectedConfig] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        fetchCalibrations();
    }, []);

    const fetchCalibrations = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/system/calibrations', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            const data = await response.json();
            setCalibrations(data);
            if (data.length > 0 && !selectedConfig) {
                setSelectedConfig(data.find(c => c.is_active) || data[0]);
            }
        } catch (err) {
            console.error("Error fetching calibrations:", err);
        }
    };

    const handleDeploy = async (id) => {
        try {
            await fetch(`http://localhost:8000/api/system/calibrations/${id}/activate`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            fetchCalibrations();
            alert("Configuration Deployed! Dashboard updated.");
        } catch (err) {
            console.error("Error deploying calibration:", err);
        }
    };

    const renderPreview = (config) => {
        if (!config) return null;
        let points = { map: [] };
        try {
            points = JSON.parse(config.points);
        } catch (e) { }

        return (
            <div style={{ position: 'relative', width: '100%', height: '300px', background: '#020617', borderRadius: '0.5rem', overflow: 'hidden', border: '2px solid #3b82f6' }}>
                <img src="/floor_plan.png" alt="Map Preview" style={{ width: '100%', height: '100%', objectFit: 'contain', opacity: 0.4 }} />
                {points.map && points.map.map((p, i) => (
                    <div key={i} style={{
                        position: 'absolute',
                        left: `${p.x * 100}%`,
                        top: `${p.y * 100}%`,
                        width: '10px', height: '10px',
                        background: '#3b82f6', borderRadius: '50%',
                        border: '2px solid white',
                        transform: 'translate(-50%, -50%)'
                    }} />
                ))}
                <div style={{ position: 'absolute', bottom: '10px', left: '10px', background: 'rgba(0,0,0,0.7)', padding: '4px 8px', borderRadius: '4px', fontSize: '0.75rem' }}>
                    Signature: {config.name} ({points.map ? points.map.length : 0} points)
                </div>
            </div>
        );
    };

    return (
        <div style={{ padding: '2rem', background: '#0f172a', minHeight: '100vh', color: 'white' }}>
            <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                    <h1>POV Configuration Library</h1>
                    <div style={{ display: 'flex', gap: '1rem' }}>
                        <button onClick={() => navigate('/dashboard')} style={{ background: '#1e293b', color: 'white', border: 'none', padding: '0.6rem 1.2rem', borderRadius: '0.5rem', cursor: 'pointer' }}>Dashboard</button>
                        <button onClick={() => navigate('/calibrate')} style={{ background: '#3b82f6', color: 'white', border: 'none', padding: '0.6rem 1.2rem', borderRadius: '0.5rem', cursor: 'pointer' }}>New Setup</button>
                    </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '2rem' }}>
                    {/* List Section */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem', alignContent: 'start' }}>
                        {calibrations.map((cal) => (
                            <div
                                key={cal.id}
                                onClick={() => setSelectedConfig(cal)}
                                style={{
                                    background: selectedConfig?.id === cal.id ? '#1e293b' : '#111827',
                                    padding: '1.5rem',
                                    borderRadius: '1rem',
                                    cursor: 'pointer',
                                    border: cal.is_active ? '2px solid #10b981' : '1px solid #334155',
                                    transition: 'all 0.2s'
                                }}
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                    <h3 style={{ margin: 0 }}>{cal.name}</h3>
                                    {cal.is_active && <span style={{ color: '#10b981', fontSize: '0.75rem', fontWeight: 'bold' }}>ACTIVE</span>}
                                </div>
                                <p style={{ color: '#64748b', fontSize: '0.8rem' }}>Added: {new Date(cal.created_at).toLocaleDateString()}</p>
                            </div>
                        ))}
                    </div>

                    {/* Preview Section */}
                    <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '1rem', border: '1px solid #334155', alignSelf: 'start' }}>
                        <h2 style={{ marginBottom: '1.5rem' }}>POV Preview</h2>
                        {selectedConfig ? (
                            <>
                                {renderPreview(selectedConfig)}
                                <div style={{ marginTop: '2rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                    <button
                                        onClick={() => handleDeploy(selectedConfig.id)}
                                        disabled={selectedConfig.is_active}
                                        style={{
                                            padding: '1rem',
                                            background: selectedConfig.is_active ? '#334155' : '#10b981',
                                            color: 'white', border: 'none', borderRadius: '0.5rem',
                                            fontWeight: 'bold', cursor: selectedConfig.is_active ? 'default' : 'pointer'
                                        }}
                                    >
                                        Deploy Configuration
                                    </button>
                                    <button
                                        onClick={() => navigate('/calibrate', { state: { calibration: selectedConfig } })}
                                        style={{ padding: '0.8rem', background: 'transparent', color: '#94a3b8', border: '1px solid #334155', borderRadius: '0.5rem', cursor: 'pointer' }}
                                    >
                                        Edit / Fine-tune
                                    </button>
                                </div>
                            </>
                        ) : (
                            <div style={{ textAlign: 'center', color: '#64748b', padding: '3rem' }}>Select a config to preview</div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ConfigurationLibrary;
