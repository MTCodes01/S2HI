import React from 'react';
import ImprovementGraph from './ImprovementGraph';

interface ReportTemplateProps {
    studentData: any;
    historyData: any[];
    period: string;
}

const ReportTemplate = React.forwardRef<HTMLDivElement, ReportTemplateProps>(({ studentData, historyData, period }, ref) => {

    const getAccuracyLevel = (accuracy: number) => {
        if (accuracy >= 85) return { label: 'Excellent', color: '#059669', bg: '#ecfdf5' };
        if (accuracy >= 70) return { label: 'Good', color: '#2563eb', bg: '#eff6ff' };
        if (accuracy >= 50) return { label: 'Borderline', color: '#d97706', bg: '#fffbeb' };
        return { label: 'At Risk', color: '#dc2626', bg: '#fef2f2' };
    };

    const styles = {
        container: {
            width: '210mm',
            minHeight: '297mm',
            padding: '20mm',
            background: 'white',
            color: '#0f172a',
            fontFamily: "'Inter', sans-serif",
            boxSizing: 'border-box' as const,
            position: 'absolute' as const,
            top: '-20000px', // Way out of sight
            left: '-20000px',
        },
        header: {
            borderBottom: '3px solid #0f172a',
            paddingBottom: '15px',
            marginBottom: '30px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            backgroundColor: 'white'
        },
        titleBox: {
            flex: 1
        },
        title: {
            fontSize: '28px',
            fontWeight: 900,
            color: '#0f172a',
            margin: 0,
            letterSpacing: '-0.02em'
        },
        subtitle: {
            fontSize: '14px',
            color: '#64748b',
            marginTop: '4px',
            fontWeight: 500,
            textTransform: 'uppercase' as const,
            letterSpacing: '0.05em'
        },
        metadataGrid: {
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '15px',
            marginBottom: '40px',
            backgroundColor: '#f8fafc',
            padding: '20px',
            borderRadius: '12px',
            border: '1px solid #e2e8f0'
        },
        metaItem: {
            display: 'flex',
            flexDirection: 'column' as const,
            gap: '4px',
            backgroundColor: '#f8fafc'
        },
        metaLabel: {
            fontSize: '11px',
            fontWeight: 700,
            color: '#64748b',
            textTransform: 'uppercase' as const
        },
        metaValue: {
            fontSize: '15px',
            fontWeight: 600,
            color: '#0f172a'
        },
        section: {
            marginBottom: '40px',
            backgroundColor: 'white',
            position: 'relative' as const,
        },
        sectionHeader: {
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            marginBottom: '20px',
            borderBottom: '1px solid #e2e8f0',
            paddingBottom: '10px'
        },
        sectionTitle: {
            fontSize: '18px',
            fontWeight: 800,
            color: '#0f172a',
            margin: 0
        },
        summaryBox: {
            fontSize: '14px',
            lineHeight: 1.6,
            color: '#334155',
            backgroundColor: '#f1f5f9',
            padding: '20px',
            borderRadius: '10px',
            borderLeft: '5px solid #3b82f6'
        },
        insightList: {
            listStyle: 'none',
            padding: 0,
            margin: 0,
            display: 'flex',
            flexDirection: 'column' as const,
            gap: '12px'
        },
        insightItem: {
            fontSize: '14px',
            display: 'flex',
            gap: '12px',
            alignItems: 'flex-start'
        },
        insightBullet: {
            color: '#3b82f6',
            fontWeight: 900,
            fontSize: '18px',
            marginTop: '-2px'
        },
        domainTable: {
            width: '100%',
            borderCollapse: 'collapse' as const,
            marginTop: '10px'
        },
        tableHeader: {
            textAlign: 'left' as const,
            fontSize: '11px',
            fontWeight: 700,
            color: '#64748b',
            textTransform: 'uppercase' as const,
            padding: '12px 15px',
            backgroundColor: '#f8fafc',
            borderBottom: '2px solid #e2e8f0'
        },
        tableCell: {
            padding: '15px',
            borderBottom: '1px solid #f1f5f9',
            fontSize: '14px'
        },
        badge: {
            padding: '4px 10px',
            borderRadius: '6px',
            fontSize: '12px',
            fontWeight: 700,
            display: 'inline-block'
        },
        stepItem: {
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '12px',
            backgroundColor: 'white',
            border: '1px solid #e2e8f0',
            borderRadius: '8px',
            marginBottom: '10px',
            fontSize: '14px'
        },
        stepNumber: {
            width: '24px',
            height: '24px',
            backgroundColor: '#0f172a',
            color: 'white',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '12px',
            fontWeight: 700,
            flexShrink: 0
        },
        signatoryRow: {
            marginTop: '60px',
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '60px'
        },
        signLine: {
            borderTop: '1px solid #0f172a',
            paddingTop: '8px',
            fontSize: '12px',
            fontWeight: 600,
            color: '#64748b'
        },
        footer: {
            marginTop: '60px',
            paddingTop: '20px',
            borderTop: '1px solid #e2e8f0',
            fontSize: '11px',
            color: '#94a3b8',
            textAlign: 'center' as const,
            lineHeight: 1.5
        }
    };

    return (
        <div ref={ref} style={styles.container}>
            {/* Header */}
            <div style={styles.header}>
                <div style={styles.titleBox}>
                    <h1 style={styles.title}>SCREENING EVALUATION REPORT</h1>
                    <p style={styles.subtitle}>S2HI Learning Assessment System • Confidential</p>
                </div>
                <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '24px', fontWeight: 900, color: '#3b82f6' }}>S2HI</div>
                    <div style={{ fontSize: '10px', color: '#94a3b8' }}>Professional Edition</div>
                </div>
            </div>

            {/* Metadata */}
            <div style={styles.metadataGrid} className="nobreak">
                <div style={styles.metaItem}>
                    <span style={styles.metaLabel}>Student Identification</span>
                    <span style={styles.metaValue}>{studentData.studentId}</span>
                </div>
                <div style={styles.metaItem}>
                    <span style={styles.metaLabel}>Developmental Stage</span>
                    <span style={styles.metaValue}>{studentData.ageGroup} Years</span>
                </div>
                <div style={styles.metaItem}>
                    <span style={styles.metaLabel}>Evaluation Date</span>
                    <span style={styles.metaValue}>{studentData.assessmentDate}</span>
                </div>
                <div style={styles.metaItem}>
                    <span style={styles.metaLabel}>Risk Indication</span>
                    <span style={{ ...styles.metaValue, color: studentData.riskLevel > 15 ? '#dc2626' : '#059669' }}>
                        {studentData.finalRisk}
                    </span>
                </div>
                <div style={styles.metaItem}>
                    <span style={styles.metaLabel}>Subjective Confidence</span>
                    <span style={styles.metaValue}>{studentData.confidence}</span>
                </div>
                <div style={styles.metaItem}>
                    <span style={styles.metaLabel}>Evaluation Scope</span>
                    <span style={styles.metaValue}>{period} Evaluation</span>
                </div>
                <div style={styles.metaItem}>
                    <span style={styles.metaLabel}>Report Status</span>
                    <span style={styles.metaValue}>Finalised</span>
                </div>
            </div>

            {/* Summary */}
            <section style={styles.section} className="nobreak">
                <div style={styles.sectionHeader}>
                    <h2 style={styles.sectionTitle}>I. EXECUTIVE SUMMARY</h2>
                </div>
                <div style={styles.summaryBox}>
                    {studentData.summary}
                </div>
            </section>

            {/* Key Insights */}
            {studentData.keyInsights && studentData.keyInsights.length > 0 && (
                <section style={styles.section} className="nobreak">
                    <div style={styles.sectionHeader}>
                        <h2 style={styles.sectionTitle}>II. CLINICAL INSIGHTS</h2>
                    </div>
                    <ul style={styles.insightList}>
                        {studentData.keyInsights.map((insight: string, i: number) => (
                            <li key={i} style={styles.insightItem}>
                                <span style={styles.insightBullet}>•</span>
                                <span>{insight}</span>
                            </li>
                        ))}
                    </ul>
                </section>
            )}

            {/* Domain Performance */}
            <section style={styles.section} className="nobreak">
                <div style={styles.sectionHeader}>
                    <h2 style={styles.sectionTitle}>III. DOMAIN-SPECIFIC ANALYSIS</h2>
                </div>
                <table style={styles.domainTable}>
                    <thead>
                        <tr>
                            <th style={styles.tableHeader}>Assessment Domain</th>
                            <th style={styles.tableHeader}>Proficiency</th>
                            <th style={styles.tableHeader}>Latency</th>
                            <th style={styles.tableHeader}>Clinical Recommendation</th>
                        </tr>
                    </thead>
                    <tbody>
                        {Object.entries(studentData.patterns).map(([domain, data]: [string, any]) => {
                            const level = getAccuracyLevel(data.accuracy);
                            return (
                                <tr key={domain}>
                                    <td style={{ ...styles.tableCell, fontWeight: 700, textTransform: 'capitalize' }}>{domain}</td>
                                    <td style={styles.tableCell}>
                                        <div style={{
                                            ...styles.badge,
                                            backgroundColor: level.bg,
                                            color: level.color
                                        }}>
                                            {data.accuracy}% - {level.label}
                                        </div>
                                    </td>
                                    <td style={styles.tableCell}>{(data.avgTime / 1000).toFixed(2)}s</td>
                                    <td style={{ ...styles.tableCell, fontSize: '13px', color: '#475569' }}>{data.recommendation}</td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </section>

            {/* Next Steps */}
            {studentData.nextSteps && studentData.nextSteps.length > 0 && (
                <section style={styles.section} className="nobreak">
                    <div style={styles.sectionHeader}>
                        <h2 style={styles.sectionTitle}>IV. INTERVENTION PLAN</h2>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '10px' }}>
                        {studentData.nextSteps.map((step: string, i: number) => (
                            <div key={i} style={styles.stepItem}>
                                <div style={styles.stepNumber}>{i + 1}</div>
                                <span>{step}</span>
                            </div>
                        ))}
                    </div>
                </section>
            )}

            {/* Progress Graph */}
            {historyData.length > 0 && (
                <section style={styles.section} className="nobreak">
                    <div style={styles.sectionHeader}>
                        <h2 style={styles.sectionTitle}>V. LONGITUDINAL PROGRESSION</h2>
                    </div>
                    <div style={{ height: '350px', width: '100%', padding: '20px', border: '1px solid #e2e8f0', borderRadius: '12px', backgroundColor: 'white' }}>
                        <ImprovementGraph data={historyData} isReport={true} />
                    </div>
                </section>
            )}

            {/* Footer */}
            <footer style={styles.footer}>
                <p><strong>Clinical Disclaimer:</strong> This report is generated by an algorithmic screening system and is intended for informational and educational purposes only. It does not constitute a formal clinical diagnosis of Dyslexia, Dyscalculia, or ADHD. Final diagnostic conclusions must be made by a qualified healthcare professional or educational psychologist based on a comprehensive multi-battery evaluation.</p>
                <p style={{ marginTop: '10px' }}>S2HI High-Impact Learning Assessment Systems • Confidential Document • &copy; {new Date().getFullYear()}</p>
            </footer>
        </div>
    );
});

export default ReportTemplate;
