import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Register() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleRegister = async (e) => {
        e.preventDefault();
        setError('');
        try {
            const response = await fetch('http://localhost:8000/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            if (response.ok) {
                // Auto login or redirect to login
                navigate('/login');
            } else {
                const data = await response.json();
                setError(data.detail || "Registration failed");
            }
        } catch (err) {
            console.error(err);
            setError("Server error");
        }
    };

    return (
        <div className="login-container">
            <div className="login-card">
                <h1>Sentinel Pro</h1>
                <p className="subtitle">Create New Account</p>

                {error && <div className="error-message">{error}</div>}

                <form onSubmit={handleRegister}>
                    <div className="input-group">
                        <label>Username</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Enter username"
                            required
                        />
                    </div>
                    <div className="input-group">
                        <label>Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter password"
                            required
                        />
                    </div>
                    <button type="submit" className="login-btn">Register</button>
                    <p style={{ marginTop: '1rem', textAlign: 'center' }}>
                        <a href="/login" style={{ color: '#646cff' }}>Already have an account? Login</a>
                    </p>
                </form>
            </div>
        </div>
    );
}
