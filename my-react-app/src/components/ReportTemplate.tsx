import React from 'react';
import ImprovementGraph from './ImprovementGraph';

interface ReportTemplateProps {
    studentData: any;
    historyData: any[];
    period: string;
}

const ReportTemplate = React.forwardRef<HTMLDivElement, ReportTemplateProps>(({ studentData, historyData, period }, ref) => {

    const getAccuracyLevel = (accuracy: number) => {
        if (accuracy >= 85) return { label: 'Excellent', color: '#10b981' };
        if (accuracy >= 70) return { label: 'Good', color: '#3b82f6' };
        if (accuracy >= 50) return { label: 'Needs Work', color: '#f59e0b' };
        return { label: 'Critical', color: '#ef4444' };
    };

    const styles = {
        container: {
            width: '210mm',
            minHeight: '297mm',
            padding: '20mm',
            background: 'white',
            color: '#1e293b',
            fontFamily: 'Inter, sans-serif',
            boxSizing: 'border-box' as const,
            position: 'absolute' as const,
            top: '-10000px',
            left: '-10000px',
        },
        header: {
            borderBottom: '2px solid #f1f5f9',
            paddingBottom: '20px',
            marginBottom: '30px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'baseline'
        },
        title: {
            fontSize: '24px',
            fontWeight: 800,
            color: '#0f172a',
            margin: 0
        },
        subtitle: {
            fontSize: '14px',
            color: '#64748b',
            marginTop: '4px'
        },
        section: {
            marginBottom: '30px'
        },
        sectionTitle: {
            fontSize: '16px',
            fontWeight: 700,
            color: '#334155',
            borderLeft: '4px solid #3b82f6',
            paddingLeft: '10px',
            marginBottom: '15px'
        },
        grid: {
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '20px',
            marginBottom: '20px'
        },
        card: {
            border: '1px solid #e2e8f0',
            borderRadius: '8px',
            padding: '15px',
            backgroundColor: '#f8fafc'
        },
        label: {
            fontSize: '12px',
            color: '#64748b',
            marginBottom: '4px',
            display: 'block'
        },
        value: {
            fontSize: '16px',
            fontWeight: 600,
            color: '#0f172a'
        },
        domainGrid: {
            display: 'grid',
            gridTemplateColumns: '1fr 1fr 1fr',
            gap: '15px',
            marginTop: '15px'
        },
        domainCard: {
            border: '1px solid #e2e8f0',
            borderRadius: '8px',
            padding: '15px',
            textAlign: 'center' as const
        },
        domainTitle: {
            fontSize: '14px',
            fontWeight: 700,
            marginBottom: '10px',
            display: 'block',
            textTransform: 'capitalize' as const
        },
        accuracyCircle: {
            width: '60px',
            height: '60px',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 10px',
            border: '4px solid',
            fontWeight: 700
        },
        recommendationBox: {
            backgroundColor: '#f0f9ff',
            border: '1px solid #bae6fd',
            borderRadius: '8px',
            padding: '15px',
            marginTop: '10px'
        },
        footer: {
            marginTop: '50px',
            paddingTop: '20px',
            borderTop: '1px solid #f1f5f9',
            fontSize: '10px',
            color: '#94a3b8',
            textAlign: 'center' as const
        }
    };

    return (
        <div ref={ref} style={styles.container}>
            <div style={styles.header}>
                <div>
                    <h1 style={styles.title}>Learning Assessment Report</h1>
                    <p style={styles.subtitle}>Generated on {new Date().toLocaleDateString()} • {period}</p>
                </div>
                <div style={{ textAlign: 'right' }}>
                    <span style={styles.label}>Student ID</span>
                    <span style={styles.value}>{studentData.studentId}</span>
                </div>
            </div>

            <div style={styles.grid}>
                <div style={styles.card}>
                    <span style={styles.label}>Age Group</span>
                    <span style={styles.value}>{studentData.ageGroup} years</span>
                </div>
                <div style={styles.card}>
                    <span style={styles.label}>Assessment Date</span>
                    <span style={styles.value}>{studentData.assessmentDate}</span>
                </div>
                <div style={styles.card}>
                    <span style={styles.label}>Risk Level</span>
                    <span style={{ ...styles.value, color: studentData.riskLevel > 0 ? '#ef4444' : '#10b981' }}>
                        {studentData.finalRisk} {studentData.riskLevel > 0 ? `(${studentData.riskLevel}%)` : ''}
                    </span>
                </div>
                <div style={styles.card}>
                    <span style={styles.label}>Confidence Score</span>
                    <span style={styles.value}>{studentData.confidence}</span>
                </div>
            </div>

            <div style={{ ...styles.section, marginBottom: '50px' }}>
                <h3 style={styles.sectionTitle}>Performance Summary</h3>
                <p style={{ lineHeight: 1.6, fontSize: '14px' }}>{studentData.summary}</p>

                <div style={styles.domainGrid}>
                    {Object.entries(studentData.patterns).map(([domain, data]: [string, any]) => {
                        const level = getAccuracyLevel(data.accuracy);
                        return (
                            <div key={domain} style={styles.domainCard} className="nobreak">
                                <span style={styles.domainTitle}>{domain}</span>
                                <div style={{
                                    ...styles.accuracyCircle,
                                    borderColor: level.color,
                                    color: level.color
                                }}>
                                    {data.accuracy}%
                                </div>
                                <span style={{ fontSize: '12px', color: level.color, fontWeight: 600 }}>
                                    {level.label}
                                </span>
                            </div>
                        );
                    })}
                </div>
            </div>

            <div style={styles.section}>
                <h3 style={styles.sectionTitle}>Detailed Analysis & Recommendations</h3>
                {Object.entries(studentData.patterns).map(([domain, data]: [string, any]) => (
                    <div key={domain} style={{ marginBottom: '15px' }} className="nobreak">
                        <h4 style={{ fontSize: '14px', fontWeight: 700, margin: '0 0 5px 0', textTransform: 'capitalize' }}>{domain}</h4>
                        <div style={styles.recommendationBox}>
                            <p style={{ margin: 0, fontSize: '13px', lineHeight: 1.5 }}>
                                <strong>Observations:</strong> {data.commonMistake !== 'None' ? data.commonMistake : 'Performance is consistent.'}
                            </p>
                            <p style={{ margin: '8px 0 0 0', fontSize: '13px', lineHeight: 1.5 }}>
                                <strong>Recommendation:</strong> {data.recommendation}
                            </p>
                        </div>
                    </div>
                ))}
            </div>

            {historyData.length > 0 && (
                <div style={styles.section}>
                    <h3 style={styles.sectionTitle}>Progress Over Time</h3>
                    <div style={{ height: '300px', width: '100%', marginBottom: '20px' }}>
                        <ImprovementGraph data={historyData} />
                    </div>
                </div>
            )}

            <div style={{ ...styles.footer, marginTop: '470px' }}>
                <p>This report is an early screening tool and does not constitute a medical diagnosis. Please consult with a qualified specialist for comprehensive evaluation.</p>
                <p>&copy; {new Date().getFullYear()} S2HI Learning Assessment System</p>
            </div>
        </div>
    );
});

export default ReportTemplate;
