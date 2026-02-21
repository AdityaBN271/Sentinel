import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const ConfigurationManager = () => {
    const [calibrations, setCalibrations] = useState([]);
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
        } catch (err) {
            console.error("Error fetching calibrations:", err);
        }
    };

    const handleActivate = async (id) => {
        try {
            await fetch(`http://localhost:8000/api/system/calibrations/${id}/activate`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            fetchCalibrations();
        } catch (err) {
            console.error("Error activating calibration:", err);
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Delete this calibration?")) return;
        try {
            await fetch(`http://localhost:8000/api/system/calibrations/${id}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            fetchCalibrations();
        } catch (err) {
            console.error("Error deleting calibration:", err);
        }
    };

    return (
        <div style={{ padding: '2rem', background: '#0f172a', minHeight: '100vh', color: 'white' }}>
            <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                    <h1>Configuration Library</h1>
                    <button
                        onClick={() => navigate('/dashboard')}
                        style={{ background: '#1e293b', color: 'white', border: 'none', padding: '0.5rem 1rem', borderRadius: '0.5rem', cursor: 'pointer' }}
                    >
                        Back to Dashboard
                    </button>
                    <button
                        onClick={() => navigate('/calibrate')}
                        style={{ background: '#3b82f6', color: 'white', border: 'none', padding: '0.5rem 1rem', borderRadius: '0.5rem', cursor: 'pointer' }}
                    >
                        New Calibration
                    </button>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
                    {calibrations.map((cal) => (
                        <div key={cal.id} style={{
                            background: '#1e293b',
                            padding: '1.5rem',
                            borderRadius: '1rem',
                            border: cal.is_active ? '2px solid #3b82f6' : '1px solid #334155',
                            position: 'relative'
                        }}>
                            {cal.is_active && (
                                <span style={{ position: 'absolute', top: '10px', right: '10px', background: '#3b82f6', fontSize: '0.75rem', padding: '2px 8px', borderRadius: '1rem' }}>
                                    ACTIVE
                                </span>
                            )}
                            <h3 style={{ margin: '0 0 1rem 0' }}>{cal.name}</h3>
                            <p style={{ color: '#94a3b8', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
                                Created: {new Date(cal.created_at).toLocaleDateString()}
                            </p>

                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                <button
                                    onClick={() => handleActivate(cal.id)}
                                    disabled={cal.is_active}
                                    style={{
                                        flex: 1,
                                        background: cal.is_active ? '#334155' : '#10b981',
                                        color: 'white', border: 'none', padding: '0.5rem', borderRadius: '0.5rem', cursor: cal.is_active ? 'default' : 'pointer'
                                    }}
                                >
                                    Activate
                                </button>
                                <button
                                    onClick={() => navigate('/calibrate', { state: { calibration: cal } })}
                                    style={{ flex: 1, background: '#6366f1', color: 'white', border: 'none', padding: '0.5rem', borderRadius: '0.5rem', cursor: 'pointer' }}
                                >
                                    Fine-tune
                                </button>
                                <button
                                    onClick={() => handleDelete(cal.id)}
                                    style={{ background: '#ef4444', color: 'white', border: 'none', padding: '0.5rem 1rem', borderRadius: '0.5rem', cursor: 'pointer' }}
                                >
                                    🗑️
                                </button>
                            </div>
                        </div>
                    ))}
                    {calibrations.length === 0 && (
                        <div style={{ gridColumn: '1/-1', textAlign: 'center', padding: '4rem', color: '#64748b' }}>
                            <h3>No calibrations found. Click "New Calibration" to get started.</h3>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ConfigurationManager;
