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

interface HistoryData {
    date: string;       // "YYYY-MM-DD"
    time?: string;      // "HH:MM AM/PM"
    datetime?: string;  // ISO string
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
        const dateStr = dataPoint.datetime
            ? new Date(dataPoint.datetime).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })
            : dataPoint.date;
        const timeStr = dataPoint.datetime
            ? new Date(dataPoint.datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            : dataPoint.time || '';

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
                    <p style={{ fontSize: '0.8rem', margin: 0, color: '#64748b' }}>{timeStr}</p>
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
                            {(entry.value * 100).toFixed(0)}%
                        </span>
                    </div>
                ))}

                <div style={{ marginTop: '0.8rem', paddingTop: '0.5rem', borderTop: '1px solid #eee' }}>
                    <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#94a3b8', letterSpacing: '0.5px' }}>Overall Result</span>
                    <p style={{ margin: '2px 0 0 0', fontSize: '0.85rem', fontWeight: 600, color: '#334155' }}>
                        {dataPoint.risk_label.replace(/-/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}
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
            <div style={{
                height: '400px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexDirection: 'column',
                color: 'var(--text-muted)',
                background: 'var(--glass-bg)',
                borderRadius: '24px',
                border: '1px solid var(--glass-border)'
            }}>
                <p>No history data available yet.</p>
            </div>
        );
    }

    // Sort data chronologically
    const sortedData = [...data].sort((a, b) => {
        const dateA = a.datetime ? new Date(a.datetime).getTime() : new Date(a.date).getTime();
        const dateB = b.datetime ? new Date(b.datetime).getTime() : new Date(b.date).getTime();
        return dateA - dateB;
    });

    // Group data by date to manage spacing
    const groupedData: any[] = [];
    let lastDate = '';

    sortedData.forEach((item, index) => {
        const dateObj = item.datetime ? new Date(item.datetime) : new Date(item.date);
        const currentDate = dateObj.toLocaleDateString();

        // Add spacer if date changes (but not at the start)
        if (lastDate && lastDate !== currentDate) {
            groupedData.push({ uniqueId: `spacer-${index}`, isSpacer: true });
        }

        groupedData.push({
            ...item,
            uniqueId: `${index}_${dateObj.getTime()}`,
            // Show tick label only for the first item of the day, or if it's the only one
            tickLabel: lastDate !== currentDate ? dateObj.toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : '',
            timestamp: dateObj.getTime(),
            isSpacer: false
        });

        lastDate = currentDate;
    });

    return (
        <div style={{ width: '100%', height: 450 }}>
            <ResponsiveContainer>
                <LineChart
                    data={sortedData} // Use sorted data directly, line charts handle time better
                    margin={{
                        top: 20,
                        right: 30, // More right margin for labels
                        left: 0,
                        bottom: 20,
                    }}
                >
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.05)" vertical={false} />

                    <XAxis
                        dataKey={(item) => item.datetime ? new Date(item.datetime).getTime() : new Date(item.date).getTime()}
                        domain={['auto', 'auto']}
                        tickFormatter={(unixTime) => new Date(unixTime).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                        type="number" // Use time scale
                        scale="time"
                        stroke="var(--text-muted)"
                        tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
                        tickLine={false}
                        axisLine={false}
                        dy={10}
                    />

                    <YAxis
                        stroke="var(--text-muted)"
                        tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
                        tickLine={false}
                        axisLine={false}
                        domain={[0, 1]}
                        tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                    />

                    <Tooltip
                        content={<CustomTooltip />}
                        cursor={{ stroke: 'rgba(0,0,0,0.1)', strokeWidth: 2 }}
                    />

                    <Legend
                        verticalAlign="top"
                        height={36}
                        iconType="circle"
                        wrapperStyle={{ paddingBottom: '20px' }}
                    />

                    {/* Risk Threshold Lines */}
                    <ReferenceLine y={0.8} stroke="rgba(16, 185, 129, 0.4)" strokeDasharray="3 3" label={{ position: 'right', value: 'Excellent', fill: '#10b981', fontSize: 10 }} />
                    <ReferenceLine y={0.5} stroke="rgba(245, 158, 11, 0.4)" strokeDasharray="3 3" label={{ position: 'right', value: 'Needs Work', fill: '#f59e0b', fontSize: 10 }} />

                    <Line
                        type="monotone"
                        dataKey="dyslexia_score"
                        name="Reading"
                        stroke="#3b82f6"
                        strokeWidth={3}
                        dot={{ r: 4, fill: '#3b82f6', strokeWidth: 2, stroke: '#fff' }}
                        activeDot={{ r: 6 }}
                        connectNulls
                    />
                    <Line
                        type="monotone"
                        dataKey="dyscalculia_score"
                        name="Math"
                        stroke="#10b981"
                        strokeWidth={3}
                        dot={{ r: 4, fill: '#10b981', strokeWidth: 2, stroke: '#fff' }}
                        activeDot={{ r: 6 }}
                        connectNulls
                    />
                    <Line
                        type="monotone"
                        dataKey="attention_score"
                        name="Focus"
                        stroke="#8b5cf6"
                        strokeWidth={3}
                        dot={{ r: 4, fill: '#8b5cf6', strokeWidth: 2, stroke: '#fff' }}
                        activeDot={{ r: 6 }}
                        connectNulls
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default ImprovementGraph;
