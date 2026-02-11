import React from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Legend } from 'recharts';

const TrendAnalysisChart = ({ data }) => {
    if (!data || data.length === 0) return <div style={{ color: '#888', textAlign: 'center', padding: '2rem' }}>No trend data available</div>;

    return (
        <ResponsiveContainer width="100%" height={250}>
            <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                <XAxis dataKey="timestamp" stroke="#94a3b8" tick={{ fontSize: 10 }} />
                <YAxis stroke="#94a3b8" />
                <Tooltip
                    contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f1f5f9' }}
                    labelStyle={{ color: '#94a3b8' }}
                />
                <Legend verticalAlign="top" height={36} />
                <Line type="monotone" dataKey="count" stroke="#94a3b8" dot={false} strokeWidth={1} name="Raw Count" isAnimationActive={false} />
                <Line type="monotone" dataKey="moving_avg" stroke="#22c55e" strokeWidth={2} name="Moving Avg (Trend)" dot={false} />
            </LineChart>
        </ResponsiveContainer>
    );
};

export default TrendAnalysisChart;
