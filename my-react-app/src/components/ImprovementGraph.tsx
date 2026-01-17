import React from 'react';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    ReferenceLine
} from 'recharts';

// --- PASTE STARTS HERE ---

interface HistoryData {
    date: string;       
    time?: string;      
    datetime?: string;  
    dyslexia_score: number;
    dyscalculia_score: number;
    attention_score: number;
    risk_label: string;
}

interface ImprovementGraphProps {
    data: HistoryData[];
}

const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
        const dataPoint = payload[0].payload;
        
        // UPDATED: Use the date string directly from the parent
        // This ensures "Jan 17 (1)" displays correctly instead of being re-converted to a date object
        const dateStr = dataPoint.date; 
        const timeStr = dataPoint.time || '';

        return (
            <div className="glass-panel" style={{
                padding: '1rem',
                border: '1px solid rgba(255,255,255,0.5)',
                background: 'rgba(255, 255, 255, 0.95)',
                boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
                minWidth: '200px'
            }}>
                <div style={{ marginBottom: '0.8rem', borderBottom: '1px solid #eee', paddingBottom: '0.5rem' }}>
                    <p style={{ fontWeight: 'bold', margin: 0, color: '#334155' }}>{dateStr}</p>
                    {timeStr && <p style={{ fontSize: '0.8rem', margin: 0, color: '#64748b' }}>{timeStr}</p>}
                </div>

                {payload.map((entry: any, index: number) => (
                    <div key={index} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <div style={{ width: '8px', height: '8px', borderRadius: '2px', backgroundColor: entry.color }}></div>
                            <span style={{ fontSize: '0.9rem', color: '#475569' }}>
                                {entry.name}:
                            </span>
                        </div>
                        <span style={{ fontWeight: 'bold', color: entry.color }}>
                            {(entry.value * 100).toFixed(0)}% (Proficiency)
                        </span>
                    </div>
                ))}

                <div style={{ marginTop: '0.8rem', paddingTop: '0.5rem', borderTop: '1px solid #eee' }}>
                    <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#94a3b8', letterSpacing: '0.5px' }}>Overall Result</span>
                    <p style={{ margin: '2px 0 0 0', fontSize: '0.85rem', fontWeight: 600, color: '#334155' }}>
                        {dataPoint.risk_label?.replace(/-/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()) || 'N/A'}
                    </p>
                </div>
            </div>
        );
    }
    return null;
};

const ImprovementGraph: React.FC<ImprovementGraphProps> = ({ data }) => {
    if (!data || data.length === 0) {
        return (
            <div style={{ height: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', color: 'var(--text-muted)', background: 'var(--glass-bg)', borderRadius: '24px', border: '1px solid var(--glass-border)' }}>
                <p>No history data available yet.</p>
            </div>
        );
    }

    return (
        <div style={{ width: '100%', height: 450 }}>
            <ResponsiveContainer>
                <LineChart
                    data={data} // UPDATED: Use data directly (removed internal sorting/grouping)
                    margin={{ top: 20, right: 30, left: 0, bottom: 20 }}
                >
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.1)" vertical={false} />

                    {/* UPDATED: XAxis is now Categorical (Simple Strings) */}
                    {/* We removed type="number" and scale="time" here */}
                    <XAxis
                        dataKey="date" 
                        stroke="#475569"
                        tick={{ fill: '#475569', fontSize: 12, fontWeight: 500 }}
                        tickLine={false}
                        axisLine={false}
                        dy={10}
                        padding={{ left: 20, right: 20 }}
                    />

                    <YAxis
                        stroke="#475569"
                        tick={{ fill: '#475569', fontSize: 12, fontWeight: 500 }}
                        tickLine={false}
                        axisLine={false}
                        domain={[0, 1]}
                        tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                        label={{ value: 'Proficiency Score', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#64748b', fontSize: 12 } }}
                    />

                    <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'rgba(0,0,0,0.1)', strokeWidth: 2 }} />

                    <Legend verticalAlign="top" height={36} iconType="circle" wrapperStyle={{ paddingBottom: '20px' }} />

                    <ReferenceLine y={0.8} stroke="rgba(16, 185, 129, 0.4)" strokeDasharray="3 3" label={{ position: 'right', value: 'Excellent', fill: '#10b981', fontSize: 10 }} />
                    <ReferenceLine y={0.5} stroke="rgba(245, 158, 11, 0.4)" strokeDasharray="3 3" label={{ position: 'right', value: 'Needs Practice', fill: '#f59e0b', fontSize: 10 }} />

                    <Line type="monotone" dataKey="dyslexia_score" name="Reading" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4, fill: '#3b82f6', strokeWidth: 2, stroke: '#fff' }} activeDot={{ r: 6 }} connectNulls />
                    <Line type="monotone" dataKey="dyscalculia_score" name="Math" stroke="#10b981" strokeWidth={3} dot={{ r: 4, fill: '#10b981', strokeWidth: 2, stroke: '#fff' }} activeDot={{ r: 6 }} connectNulls />
                    <Line type="monotone" dataKey="attention_score" name="Focus" stroke="#8b5cf6" strokeWidth={3} dot={{ r: 4, fill: '#8b5cf6', strokeWidth: 2, stroke: '#fff' }} activeDot={{ r: 6 }} connectNulls />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default ImprovementGraph;
    // Sort data chronologically
    