import React, { useEffect, useRef, useState } from 'react';

const TacticalHeatmap = ({ detections, floorPlan }) => {
    const containerRef = useRef(null);
    const heatmapInstance = useRef(null);
    const [historySlice, setHistorySlice] = useState(100); // 100% = Latest

    useEffect(() => {
        if (!heatmapInstance.current && containerRef.current) {
            // heatmap.js is loaded via CDN in index.html
            if (window.h337) {
                heatmapInstance.current = window.h337.create({
                    container: containerRef.current,
                    radius: 25, // Mission V11 Aesthetic
                    maxOpacity: 0.7,
                    minOpacity: 0,
                    blur: 0.85, // Mission V11 Aesthetic
                    gradient: {
                        '.2': 'blue',
                        '.4': 'cyan',
                        '.6': 'lime',
                        '.8': 'yellow',
                        '.95': 'red'
                    }
                });
            }
        }
    }, []);

    useEffect(() => {
        if (heatmapInstance.current && detections && containerRef.current) {
            const width = containerRef.current.offsetWidth;
            const height = containerRef.current.offsetHeight;

            // Mission V11: Time-Travel Slicing
            const sliceCount = Math.floor((detections.length * historySlice) / 100);
            const activeDetections = detections.slice(0, sliceCount).slice(-100);

            const points = activeDetections.map(d => ({
                x: Math.floor(d.map_x * width),
                y: Math.floor(d.map_y * height),
                value: 1
            })).filter(p => !isNaN(p.x) && !isNaN(p.y) && p.x >= 0 && p.y >= 0);

            heatmapInstance.current.setData({
                max: 5,
                data: points
            });
        }
    }, [detections, historySlice]);

    return (
        <div style={{ position: 'relative', width: '100%' }}>
            <div style={{
                position: 'relative',
                width: '100%',
                height: '350px',
                background: '#020617',
                borderRadius: '0.5rem',
                overflow: 'hidden',
                border: '1px solid #1e293b'
            }}>
                <img
                    src={floorPlan || "/floor_plan.png"}
                    alt="Tactical Floor Plan"
                    style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        width: '100%',
                        height: '100%',
                        objectFit: 'contain',
                        opacity: 0.6,
                        zIndex: 0
                    }}
                />
                <div
                    ref={containerRef}
                    style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        width: '100%',
                        height: '100%',
                        zIndex: 1
                    }}
                />
            </div>

            {/* Mission V11: Time-Travel Slider */}
            <div style={{ marginTop: '1rem', background: '#1e293b', padding: '1rem', borderRadius: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.8rem', color: '#94a3b8' }}>
                    <span>Historical Time-Travel Playback</span>
                    <span style={{ color: historySlice === 100 ? '#10b981' : '#3b82f6', fontWeight: 'bold' }}>
                        {historySlice === 100 ? "LIVE" : `Rewind: ${historySlice}%`}
                    </span>
                </div>
                <input
                    type="range"
                    min="1"
                    max="100"
                    value={historySlice}
                    onChange={(e) => setHistorySlice(parseInt(e.target.value))}
                    style={{ width: '100%', cursor: 'pointer', accentColor: '#3b82f6' }}
                />
            </div>
        </div>
    );
};

export default TacticalHeatmap;
