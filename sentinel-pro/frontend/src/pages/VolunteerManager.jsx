import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const VolunteerManager = () => {
    const navigate = useNavigate();
    const [volunteers, setVolunteers] = useState([]);
    const [zones, setZones] = useState([]);
    const [newName, setNewName] = useState('');
    const [newPhone, setNewPhone] = useState('');

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const token = localStorage.getItem('token');
            const [volRes, zoneRes] = await Promise.all([
                fetch('http://localhost:8000/api/volunteers/', { headers: { 'Authorization': `Bearer ${token}` } }),
                fetch('http://localhost:8000/api/zones/', { headers: { 'Authorization': `Bearer ${token}` } })
            ]);
            setVolunteers(await volRes.json());
            setZones(await zoneRes.json());
        } catch (err) { console.error("Error fetching data", err); }
    };

    const handleAddVolunteer = async () => {
        if (!newName || !newPhone) return alert("Fill all fields");
        try {
            const res = await fetch('http://localhost:8000/api/volunteers/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({ name: newName, phone: newPhone })
            });
            if (res.ok) {
                fetchData();
                setNewName('');
                setNewPhone('');
            }
        } catch (err) { console.error("Error adding volunteer", err); }
    };

    const handleAssign = async (volId, zoneName) => {
        try {
            await fetch(`http://localhost:8000/api/volunteers/${volId}/assign?zone_name=${zoneName}`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            fetchData();
            alert(`SMS Sent to volunteer for zone: ${zoneName}`);
        } catch (err) { console.error("Error assigning zone", err); }
    };

    const handleDelete = async (id) => {
        await fetch(`http://localhost:8000/api/volunteers/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        fetchData();
    };

    return (
        <div style={{ padding: '2rem', background: '#0f172a', minHeight: '100vh', color: 'white' }}>
            <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2rem' }}>
                    <h1>Volunteer Coordination Center</h1>
                    <button onClick={() => navigate('/dashboard')} style={{ background: '#334155', border: 'none', padding: '0.5rem 1rem', color: 'white', borderRadius: '4px', cursor: 'pointer' }}>Back to Dashboard</button>
                </div>

                <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '8px', marginBottom: '2rem' }}>
                    <h3 style={{ marginBottom: '1rem' }}>Register New Volunteer</h3>
                    <div style={{ display: 'flex', gap: '1rem' }}>
                        <input placeholder="Full Name" value={newName} onChange={e => setNewName(e.target.value)} style={{ flex: 1, background: '#020617', border: '1px solid #334155', color: 'white', padding: '0.8rem', borderRadius: '4px' }} />
                        <input placeholder="Phone (with +91)" value={newPhone} onChange={e => setNewPhone(e.target.value)} style={{ flex: 1, background: '#020617', border: '1px solid #334155', color: 'white', padding: '0.8rem', borderRadius: '4px' }} />
                        <button onClick={handleAddVolunteer} style={{ background: '#3b82f6', color: 'white', border: 'none', padding: '0 2rem', borderRadius: '4px', fontWeight: 'bold', cursor: 'pointer' }}>Add</button>
                    </div>
                </div>

                <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '8px' }}>
                    <h3 style={{ marginBottom: '1.5rem' }}>Active Staff Deployment</h3>
                    <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                        <thead>
                            <tr style={{ borderBottom: '1px solid #334155', color: '#64748b', fontSize: '0.8rem' }}>
                                <th style={{ padding: '1rem' }}>NAME</th>
                                <th>PHONE</th>
                                <th>CURRENT ZONE</th>
                                <th>QUICK DEPLOY</th>
                                <th>ACTION</th>
                            </tr>
                        </thead>
                        <tbody>
                            {volunteers.map(v => (
                                <tr key={v.id} style={{ borderBottom: '1px solid #020617' }}>
                                    <td style={{ padding: '1rem', fontWeight: 'bold' }}>{v.name}</td>
                                    <td>{v.phone}</td>
                                    <td>
                                        <span style={{
                                            background: v.assigned_zone ? '#1e3a8a' : '#334155',
                                            padding: '2px 8px', borderRadius: '4px', fontSize: '0.75rem'
                                        }}>
                                            {v.assigned_zone || "Unassigned"}
                                        </span>
                                    </td>
                                    <td>
                                        <select
                                            onChange={(e) => handleAssign(v.id, e.target.value)}
                                            style={{ background: '#020617', color: 'white', border: '1px solid #334155', borderRadius: '4px', padding: '0.3rem' }}
                                            defaultValue=""
                                        >
                                            <option value="" disabled>Deploy to...</option>
                                            <option value="General Area">General Area (Whole Region)</option>
                                            {zones.map(z => <option key={z.id} value={z.name}>{z.name}</option>)}
                                        </select>
                                    </td>
                                    <td>
                                        <button onClick={() => handleDelete(v.id)} style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer' }}>Remove</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default VolunteerManager;
