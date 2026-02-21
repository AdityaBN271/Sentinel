import React from 'react';

const PerformancePulse = ({ fps, vram, device }) => {
    return (
        <div style={{
            background: '#0f172a',
            padding: '0.75rem',
            borderRadius: '0.5rem',
            border: '1px solid #1e293b',
            display: 'flex',
            gap: '1.5rem',
            alignItems: 'center',
            fontSize: '0.85rem',
            color: '#94a3b8',
            fontFamily: 'monospace'
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ color: '#3b82f6', fontWeight: 'bold' }}>⚡ ENGINE:</span>
                <span style={{ color: 'white' }}>{device || 'CPU'}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ color: '#22c55e', fontWeight: 'bold' }}>📈 FPS:</span>
                <span style={{ color: 'white' }}>{fps || 0.0}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ color: '#eab308', fontWeight: 'bold' }}>💾 VRAM:</span>
                <span style={{ color: 'white' }}>{vram || 0.0} MB</span>
            </div>
            {device === 'GPU' && (
                <div style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    background: '#22c55e',
                    boxShadow: '0 0 8px #22c55e',
                    marginLeft: 'auto'
                }} title="Hardware Acceleration Active" />
            )}
        </div>
    );
};

export default PerformancePulse;
