import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts';

const PeakHourChart = ({ data }) => {
    if (!data || data.length === 0) return <div style={{ color: '#888', textAlign: 'center', padding: '2rem' }}>No analytics data yet</div>;
    return (
        <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                <XAxis dataKey="hour" stroke="#fff" />
                <YAxis stroke="#fff" />
                <Tooltip
                    contentStyle={{ backgroundColor: '#333', borderColor: '#444', color: '#fff' }}
                    itemStyle={{ color: '#fff' }}
                />
                <Bar dataKey="count" fill="#8884d8" />
            </BarChart>
        </ResponsiveContainer>
    );
};

export default PeakHourChart;
