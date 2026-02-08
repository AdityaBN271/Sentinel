import React from 'react';

const HeatmapFn = ({ xLabels, yLabels, data }) => {
    // data is a 2D array (10x10)
    // We want to render a 10x10 grid

    // Flatten max value for color scaling
    let max = 0;
    data.forEach(row => row.forEach(val => {
        if (val > max) max = val;
    }));
    if (max === 0) max = 1; // Avoid divide by zero

    return (
        <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(10, 1fr)',
            gap: '2px',
            width: '100%',
            maxWidth: '400px', // sensible default
            aspectRatio: '1 / 1'
        }}>
            {data.flatMap((row, y) =>
                row.map((value, x) => {
                    // Calculate opacity/color
                    // Higher value = more red
                    const intensity = value / max;
                    const bgColor = `rgba(239, 68, 68, ${intensity})`; // Tailwind red-500

                    return (
                        <div
                            key={`${x}-${y}`}
                            title={`Count: ${value}`}
                            style={{
                                backgroundColor: bgColor,
                                border: '1px solid #333',
                                borderRadius: '2px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: '10px',
                                color: '#fff',
                                height: '100%',
                                width: '100%'
                            }}
                        >
                            {value > 0 ? value : ''}
                        </div>
                    );
                })
            )}
        </div>
    );
};

export default HeatmapFn;
