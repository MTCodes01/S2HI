import React from 'react';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer
} from 'recharts';

interface HistoryData {
    date: string;
    dyslexia_score: number;
    dyscalculia_score: number;
    attention_score: number;
    risk_label: string;
}

interface ImprovementGraphProps {
    data: HistoryData[];
}

const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
        return (
            <div className="glass-panel" style={{ padding: '1rem', border: '1px solid rgba(255,255,255,0.5)' }}>
                <p style={{ fontWeight: 'bold', marginBottom: '0.5rem' }}>{label}</p>
                {payload.map((entry: any, index: number) => (
                    <p key={index} style={{ color: entry.color, fontSize: '0.9rem' }}>
                        {entry.name === 'dyslexia_score' ? 'Reading Risk' :
                            entry.name === 'dyscalculia_score' ? 'Math Risk' : 'Focus Risk'}:
                        {(entry.value * 100).toFixed(0)}%
                    </p>
                ))}
                {payload[0].payload.risk_label && (
                    <p style={{ marginTop: '0.5rem', fontSize: '0.8rem', fontStyle: 'italic', color: '#64748b' }}>
                        Result: {payload[0].payload.risk_label.replace('-', ' ')}
                    </p>
                )}
            </div>
        );
    }
    return null;
};

const ImprovementGraph: React.FC<ImprovementGraphProps> = ({ data }) => {
    if (!data || data.length === 0) {
        return (
            <div style={{
                height: '300px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexDirection: 'column',
                color: 'var(--text-muted)',
                background: 'rgba(255,255,255,0.3)',
                borderRadius: '16px'
            }}>
                <p>No history data available yet.</p>
                <p style={{ fontSize: '0.9rem' }}>Complete more assessments to see your progress.</p>
            </div>
        );
    }

    // Format dates for display
    const formattedData = data.map(item => ({
        ...item,
        displayDate: new Date(item.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
    }));

    return (
        <div style={{ width: '100%', height: 350 }}>
            {data.length === 1 && (
                <div style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    zIndex: 10,
                    pointerEvents: 'none',
                    opacity: 0.7,
                    textAlign: 'center'
                }}>
                    <span style={{ background: '#eff6ff', padding: '4px 12px', borderRadius: '20px', fontSize: '0.8rem', color: '#3b82f6' }}>
                        Take more tests to see trends
                    </span>
                </div>
            )}
            <ResponsiveContainer>
                <LineChart
                    data={formattedData}
                    margin={{
                        top: 20,
                        right: 30,
                        left: 20,
                        bottom: 10,
                    }}
                >
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.05)" vertical={false} />
                    <XAxis
                        dataKey="displayDate"
                        stroke="var(--text-muted)"
                        tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
                        tickLine={false}
                        axisLine={false}
                        dy={10}
                    />
                    <YAxis
                        stroke="var(--text-muted)"
                        tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
                        tickLine={false}
                        axisLine={false}
                        domain={[0, 1]}
                        tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                    />
                    <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'rgba(0,0,0,0.1)', strokeWidth: 2 }} />
                    <Legend wrapperStyle={{ paddingTop: '20px' }} />

                    <Line
                        type="monotone"
                        dataKey="dyslexia_score"
                        name="Reading Risk"
                        stroke="#3b82f6"
                        strokeWidth={3}
                        dot={{ r: 4, strokeWidth: 2, fill: '#fff' }}
                        activeDot={{ r: 6, strokeWidth: 0 }}
                    />
                    <Line
                        type="monotone"
                        dataKey="dyscalculia_score"
                        name="Math Risk"
                        stroke="#10b981"
                        strokeWidth={3}
                        dot={{ r: 4, strokeWidth: 2, fill: '#fff' }}
                        activeDot={{ r: 6, strokeWidth: 0 }}
                    />
                    <Line
                        type="monotone"
                        dataKey="attention_score"
                        name="Focus Risk"
                        stroke="#8b5cf6"
                        strokeWidth={3}
                        dot={{ r: 4, strokeWidth: 2, fill: '#fff' }}
                        activeDot={{ r: 6, strokeWidth: 0 }}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default ImprovementGraph;
