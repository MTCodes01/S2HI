import React, { useEffect, useState } from "react";
import { useLocation, Link } from "react-router-dom";
import type { AssessmentResult, DashboardDataResponse } from "../types/types";
import { getDashboardData, getUserHistory } from "../services/api";
import ImprovementGraph from "../components/ImprovementGraph";
import "../styles/dashboard.css";

interface LocationState {
    results?: AssessmentResult;
    userId?: number;
    sessionId?: string;
    ageGroup?: string;
}

const Dashboard: React.FC = () => {
    const location = useLocation();
    const state = location.state as LocationState | null;

    const [dashboardData, setDashboardData] = useState<DashboardDataResponse | null>(null);
    const [historyData, setHistoryData] = useState<any[]>([]); // Use appropriate type
    const [showHistory, setShowHistory] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Check if we have session info to fetch real data
    const hasSessionInfo = state?.userId && state?.sessionId;

    useEffect(() => {
        const fetchDashboardData = async () => {
            if (!hasSessionInfo) return;

            setIsLoading(true);
            setError(null);

            try {
                const [data, history] = await Promise.all([
                    getDashboardData(state.userId!, state.sessionId!),
                    getUserHistory(state.userId!)
                ]);
                setDashboardData(data);
                setHistoryData(history);
            } catch (err) {
                console.error('Failed to fetch dashboard data:', err);
                setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
            } finally {
                setIsLoading(false);
            }
        };

        fetchDashboardData();
    }, [hasSessionInfo, state?.userId, state?.sessionId]);

    // ... (generateDashboardData function remains same) ...

    const generateDashboardData = () => {
        if (dashboardData) {
            // Use real data from backend
            return {
                studentId: dashboardData.student_id,
                ageGroup: dashboardData.age_group,
                finalRisk: dashboardData.final_risk,
                confidence: dashboardData.confidence,
                riskLevel: dashboardData.risk_level,
                assessmentDate: dashboardData.assessment_date,
                summary: dashboardData.summary,
                keyInsights: dashboardData.key_insights,
                patterns: {
                    reading: {
                        accuracy: dashboardData.patterns.reading.accuracy,
                        avgTime: dashboardData.patterns.reading.avg_time,
                        commonMistake: dashboardData.patterns.reading.common_mistake,
                        recommendation: dashboardData.patterns.reading.recommendation,
                    },
                    math: {
                        accuracy: dashboardData.patterns.math.accuracy,
                        avgTime: dashboardData.patterns.math.avg_time,
                        commonMistake: dashboardData.patterns.math.common_mistake,
                        recommendation: dashboardData.patterns.math.recommendation,
                    },
                    focus: {
                        accuracy: dashboardData.patterns.focus.accuracy,
                        avgTime: dashboardData.patterns.focus.avg_time,
                        commonMistake: dashboardData.patterns.focus.common_mistake,
                        recommendation: dashboardData.patterns.focus.recommendation,
                    },
                }
            };
        }

        // Demo data
        return {
            studentId: "STU-DEMO",
            ageGroup: "9–11",
            finalRisk: "Demo Mode - Complete an Assessment",
            confidence: "N/A",
            riskLevel: 0,
            assessmentDate: "No assessment completed",
            summary: "This is a demo view. Complete an assessment to see real results.",
            keyInsights: [],
            patterns: {
                reading: {
                    accuracy: 72,
                    avgTime: 1050,
                    commonMistake: "Letter Reversal (b/d, p/q)",
                    recommendation: "Use highlighted letters, phonics-based games, and short reading chunks.",
                },
                math: {
                    accuracy: 88,
                    avgTime: 720,
                    commonMistake: "None",
                    recommendation: "Math performance is strong. No immediate intervention needed.",
                },
                focus: {
                    accuracy: 75,
                    avgTime: 880,
                    commonMistake: "Impulsive clicks",
                    recommendation: "Short tasks with clear visual cues and structured breaks are helpful.",
                },
            }
        };
    };

    const hasResults = dashboardData !== null;
    const studentData = generateDashboardData();

    // ... (helper functions remain same) ...
    const getDomainIcon = (domain: string) => {
        switch (domain) {
            case 'reading': return '📚';
            case 'math': return '🔢';
            case 'focus': return '🎯';
            default: return '📊';
        }
    };

    const getAccuracyLevel = (accuracy: number) => {
        if (accuracy >= 85) return { label: 'Excellent', class: 'level-excellent' };
        if (accuracy >= 70) return { label: 'Good', class: 'level-good' };
        if (accuracy >= 50) return { label: 'Needs Work', class: 'level-warning' };
        return { label: 'Critical', class: 'level-critical' };
    };

    const getNextSteps = () => {
        if (!dashboardData) {
            return [
                { text: 'Take your first assessment to get personalized results' },
                { text: 'Results will appear here after completion' },
                { text: 'Each assessment takes about 5-10 minutes' },
            ];
        }

        return [
            { text: 'Schedule follow-up with learning specialist' },
            { text: 'Implement recommended intervention strategies' },
            { text: 'Re-assess in 4-6 weeks to track progress' },
        ];
    };

    if (isLoading) {
        return (
            <div className="dashboard-container">
                <div className="ambient-orb orb-1"></div>
                <div className="ambient-orb orb-2"></div>
                <div style={{ textAlign: 'center', padding: '4rem' }}>
                    <h2>Loading dashboard data...</h2>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="dashboard-container">
                <div className="ambient-orb orb-1"></div>
                <div className="ambient-orb orb-2"></div>
                <div style={{ textAlign: 'center', padding: '4rem' }}>
                    <h2>Error loading dashboard</h2>
                    <p>{error}</p>
                    <Link to="/" className="btn btn-primary" style={{ marginTop: '1rem' }}>
                        Return to Assessment
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="dashboard-container">
            {/* Ambient Background Elements */}
            <div className="ambient-orb orb-1"></div>
            <div className="ambient-orb orb-2"></div>

            {/* Header Section */}
            <header className="dashboard-header">
                <div className="header-content">
                    <h1 className="dashboard-title">Learning Assessment Dashboard</h1>
                    <p className="dashboard-subtitle">
                        {dashboardData ? 'Your screening results & personalized recommendations' : 'Demo view - Complete an assessment for real results'}
                    </p>
                </div>
                <div className="header-actions">
                    <button className="btn btn-secondary">
                        <span>📥</span> Export Report
                    </button>
                    <Link to="/" className="btn btn-primary">
                        <span>🔄</span> New Assessment
                    </Link>
                </div>
            </header>

            {/* No Results Banner */}
            {!dashboardData && (
                <div className="demo-banner">
                    <span>👋</span>
                    <p>
                        <strong>Demo Mode:</strong> You're viewing sample data.
                        <Link to="/"> Take an assessment</Link> to see your real results!
                    </p>
                </div>
            )}

            {/* Stats Overview Row */}
            <section className="stats-row">
                <div
                    className="stat-card"
                    onClick={() => setShowHistory(true)}
                    style={{ cursor: 'pointer', position: 'relative' }}
                    title="Click to view full history"
                >
                    <div className="stat-icon">📅</div>
                    <div className="stat-content">
                        <span className="stat-label">Assessment Date</span>
                        <span className="stat-value">{studentData.assessmentDate}</span>
                        <span style={{ fontSize: '0.7rem', color: 'var(--primary)', marginTop: '4px' }}>
                            👆 View History
                        </span>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon">🎂</div>
                    <div className="stat-content">
                        <span className="stat-label">Age Group</span>
                        <span className="stat-value">{studentData.ageGroup} years</span>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon">📊</div>
                    <div className="stat-content">
                        <span className="stat-label">Overall Score</span>
                        <span className="stat-value">
                            {Math.round(
                                (studentData.patterns.reading.accuracy +
                                    studentData.patterns.math.accuracy +
                                    studentData.patterns.focus.accuracy) / 3
                            )}%
                        </span>
                    </div>
                </div>
                <div className="stat-card highlight">
                    <div className="stat-icon">⚡</div>
                    <div className="stat-content">
                        <span className="stat-label">Risk Level</span>
                        <span className="stat-value risk-value">
                            {studentData.riskLevel > 0 ? `${studentData.riskLevel}%` : 'N/A'}
                        </span>
                    </div>
                </div>
            </section>

            {/* History Modal */}
            {showHistory && (
                <div className="modal-overlay" onClick={() => setShowHistory(false)} style={{
                    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                    background: 'rgba(0,0,0,0.5)', zIndex: 1000,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    backdropFilter: 'blur(4px)'
                }}>
                    <div className="glass-panel" onClick={e => e.stopPropagation()} style={{
                        maxWidth: '600px', width: '90%', padding: '2rem',
                        animation: 'slideUpFade 0.4s ease-out',
                        maxHeight: '80vh', overflowY: 'auto'
                    }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                            <h2 style={{ fontSize: '1.5rem', fontWeight: 800 }}>Assessment History</h2>
                            <button
                                onClick={() => setShowHistory(false)}
                                style={{ background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer' }}
                            >
                                ×
                            </button>
                        </div>

                        {historyData.length === 0 ? (
                            <p style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>No past assessments found.</p>
                        ) : (
                            <div className="history-list" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                {historyData.map((session, index) => (
                                    <div key={index} className="history-item" style={{
                                        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                        padding: '1rem',
                                        background: 'rgba(255,255,255,0.5)',
                                        border: '1px solid var(--glass-border)',
                                        borderRadius: '12px'
                                    }}>
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                                            <span style={{ fontWeight: 600, fontSize: '1rem' }}>
                                                {session.datetime ? new Date(session.datetime).toLocaleDateString() : session.date}
                                            </span>
                                            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                                                {session.datetime ? new Date(session.datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : (session.time || '12:00 PM')} • Risk: {session.risk_label}
                                            </span>
                                        </div>
                                        <button className="btn btn-sm btn-secondary" style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}>
                                            View Report
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}

                        <div style={{ marginTop: '2rem', textAlign: 'center' }}>
                            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                                Select an assessment to view detailed results.
                            </p>
                        </div>
                    </div>
                </div>
            )}



            {/* Main Content Grid ... (rest remains same) */}
            <div className="main-grid">
                {/* Left Column - Student Info */}
                <aside className="sidebar">
                    {/* Student Profile Card */}
                    <div className="card profile-card">
                        <div className="profile-header">
                            <div className="avatar">
                                <span>👤</span>
                            </div>
                            <div className="profile-info">
                                <h3>Student Profile</h3>
                                <span className="student-id">{studentData.studentId}</span>
                            </div>
                        </div>

                        <div className="profile-details">
                            <div className="detail-row">
                                <span className="detail-label">Status</span>
                                <span className={`status-badge ${hasResults ? 'warning' : 'demo'}`}>
                                    {hasResults ? studentData.finalRisk : 'No Assessment'}
                                </span>
                            </div>
                            <div className="detail-row">
                                <span className="detail-label">Confidence</span>
                                <span className="confidence-badge">{studentData.confidence}</span>
                            </div>
                        </div>
                    </div>

                    {/* Summary Card */}
                    <div className="card summary-card">
                        <h4>💡 Assessment Insight</h4>
                        <p>{studentData.summary}</p>

                        {dashboardData && studentData.keyInsights && studentData.keyInsights.length > 0 && (
                            <ul className="insights-list">
                                {studentData.keyInsights.map((insight, index) => (
                                    <li key={index}>{insight}</li>
                                ))}
                            </ul>
                        )}
                    </div>

                    {/* Next Steps Card */}
                    <div className="card next-steps-card">
                        <h4>📋 Recommended Next Steps</h4>
                        <ul className="steps-list">
                            {getNextSteps().map((step, index) => (
                                <li key={index}>
                                    <span className="step-number">{index + 1}</span>
                                    <span>{step.text}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                </aside>

                {/* Right Column - Domain Cards */}
                <main className="content-area">
                    <h2 className="section-title">
                        <span>📈</span> Domain Performance Analysis
                    </h2>

                    <div className="domain-grid">
                        {Object.entries(studentData.patterns).map(([domain, data]) => {
                            const level = getAccuracyLevel(data.accuracy);
                            return (
                                <div key={domain} className={`card domain-card domain-${domain}`}>
                                    <div className="domain-header">
                                        <div className="domain-title">
                                            <span className="domain-icon">{getDomainIcon(domain)}</span>
                                            <h3>{domain.charAt(0).toUpperCase() + domain.slice(1)}</h3>
                                        </div>
                                        <span className={`accuracy-badge ${level.class}`}>
                                            {level.label}
                                        </span>
                                    </div>

                                    {/* Accuracy Circle */}
                                    <div className="accuracy-display">
                                        <div className={`accuracy-circle ${domain}`}>
                                            <span className="accuracy-value">{data.accuracy}%</span>
                                            <span className="accuracy-label">Accuracy</span>
                                        </div>
                                    </div>

                                    {/* Metrics */}
                                    <div className="metrics-row">
                                        <div className="metric">
                                            <span className="metric-icon">⏱️</span>
                                            <div className="metric-content">
                                                <span className="metric-value">{(data.avgTime / 1000).toFixed(1)}s</span>
                                                <span className="metric-label">Avg. Time</span>
                                            </div>
                                        </div>
                                        <div className="metric">
                                            <span className="metric-icon">⚠️</span>
                                            <div className="metric-content">
                                                <span className="metric-value">{data.commonMistake === 'None' ? '—' : '1'}</span>
                                                <span className="metric-label">Issues</span>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Common Mistake */}
                                    {data.commonMistake !== 'None' && (
                                        <div className="mistake-box">
                                            <strong>Common Pattern:</strong> {data.commonMistake}
                                        </div>
                                    )}

                                    {/* Recommendation */}
                                    <div className="recommendation">
                                        <div className="recommendation-header">
                                            <span>💡</span> Teacher Tip
                                        </div>
                                        <p>{data.recommendation}</p>
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    {/* Performance Trend Graph (Moved to bottom of content area) */}
                    {hasResults && historyData.length > 0 && (
                        <div className="graph-card" style={{ marginTop: '2rem', padding: '2rem' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
                                <h2 style={{ fontSize: '1.5rem', fontWeight: 800, margin: 0 }}>Performance Trends</h2>
                                <div style={{ display: 'flex', gap: '1rem' }}>
                                    <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center' }}>
                                        <span style={{ display: 'inline-block', width: '10px', height: '10px', borderRadius: '50%', background: '#3b82f6', marginRight: '5px' }}></span>
                                        Reading
                                    </span>
                                    <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center' }}>
                                        <span style={{ display: 'inline-block', width: '10px', height: '10px', borderRadius: '50%', background: '#10b981', marginRight: '5px' }}></span>
                                        Math
                                    </span>
                                    <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center' }}>
                                        <span style={{ display: 'inline-block', width: '10px', height: '10px', borderRadius: '50%', background: '#8b5cf6', marginRight: '5px' }}></span>
                                        Focus
                                    </span>
                                </div>
                            </div>
                            <ImprovementGraph data={historyData} />
                        </div>
                    )}
                </main>
            </div>

            {/* Footer Disclaimer */}
            <footer className="disclaimer">
                <span className="disclaimer-icon">ℹ️</span>
                <p>
                    <strong>Important:</strong> This is not a medical diagnosis. It is an early screening tool
                    designed to guide educational support and professional follow-up. Please consult with
                    qualified specialists for comprehensive evaluation.
                </p>
            </footer>
        </div>
    );
};

export default Dashboard;
