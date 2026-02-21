import React, { useEffect, useRef } from 'react';

const TacticalHeatmap = ({ detections, floorPlan }) => {
    const containerRef = useRef(null);
    const heatmapInstance = useRef(null);

    useEffect(() => {
        if (!heatmapInstance.current && containerRef.current) {
            // heatmap.js is loaded via CDN in index.html
            if (window.h337) {
                heatmapInstance.current = window.h337.create({
                    container: containerRef.current,
                    radius: 20,
                    maxOpacity: 0.6,
                    minOpacity: 0.1,
                    blur: .90,
                    gradient: {
                        '.5': 'blue',
                        '.8': 'yellow',
                        '.95': 'red'
                    }
                });
            } else {
                console.error("heatmap.js (h337) not found on window");
            }
        }
    }, []);

    useEffect(() => {
        if (heatmapInstance.current && detections && containerRef.current) {
            const width = containerRef.current.offsetWidth;
            const height = containerRef.current.offsetHeight;

            // Mission V8: Limit to last 50 points for HP Laptop performance
            const recentDetections = detections.slice(-50);

            // Mission V8: Scale normalized 0.0-1.0 coords to pixel offsets
            const points = recentDetections.map(d => ({
                x: Math.floor(d.map_x * width),
                y: Math.floor(d.map_y * height),
                value: 1
            })).filter(p => !isNaN(p.x) && !isNaN(p.y) && p.x >= 0 && p.y >= 0);

            heatmapInstance.current.setData({
                max: 5, // Lower max for better sensitivity with fewer points
                data: points
            });
        }
    }, [detections]);

    return (
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
    );
};

export default TacticalHeatmap;
