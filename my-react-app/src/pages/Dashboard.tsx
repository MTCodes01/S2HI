import React from "react";
import { useLocation, Link } from "react-router-dom";
import type { AssessmentResult } from "../types/types";
import "../styles/dashboard.css";

type DomainPattern = {
    accuracy: number;
    avgTime: number;
    commonMistake: string;
    recommendation: string;
};

interface LocationState {
    results?: AssessmentResult;
    userId?: number;
    sessionId?: string;
    ageGroup?: string;
}

const Dashboard: React.FC = () => {
    const location = useLocation();
    const state = location.state as LocationState | null;

    // Check if we have real results from the assessment
    const hasResults = state?.results;

    // Generate dashboard data from results or use demo data
    const generateDashboardData = () => {
        if (hasResults && state.results) {
            const result = state.results;

            // Map risk type to display name
            const riskLabels: Record<string, string> = {
                'low-risk': 'Low Risk - No Significant Concerns',
                'dyslexia-risk': 'Possible Dyslexia-related Risk',
                'dyscalculia-risk': 'Possible Dyscalculia-related Risk',
                'attention-risk': 'Possible Attention-related Risk'
            };

            // Calculate risk percentage from confidence level
            const riskLevels: Record<string, number> = {
                'low': 30,
                'moderate': 60,
                'high': 85
            };

            return {
                studentId: state.userId ? `STU-${state.userId}` : "STU-NEW",
                ageGroup: state.ageGroup || "9–11",
                finalRisk: riskLabels[result.risk] || result.risk,
                confidence: result.confidence_level.charAt(0).toUpperCase() + result.confidence_level.slice(1),
                riskLevel: riskLevels[result.confidence_level] || 50,
                assessmentDate: new Date().toLocaleDateString('en-US', {
                    month: 'long',
                    day: 'numeric',
                    year: 'numeric'
                }),
                summary: result.key_insights.join(' ') || "Assessment completed. Review the domain analysis below for detailed insights.",
                keyInsights: result.key_insights,
                patterns: generatePatterns(result.risk)
            };
        }

        // Demo data when no results available
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

    // Generate domain patterns based on risk type
    const generatePatterns = (risk: string): Record<string, DomainPattern> => {
        const basePatterns: Record<string, DomainPattern> = {
            reading: {
                accuracy: 85,
                avgTime: 800,
                commonMistake: "None",
                recommendation: "Reading skills are developing well. Continue with current approach.",
            },
            math: {
                accuracy: 85,
                avgTime: 700,
                commonMistake: "None",
                recommendation: "Math skills are age-appropriate. Maintain regular practice.",
            },
            focus: {
                accuracy: 80,
                avgTime: 850,
                commonMistake: "None",
                recommendation: "Attention span is within normal range.",
            },
        };

        // Adjust patterns based on risk type
        switch (risk) {
            case 'dyslexia-risk':
                basePatterns.reading = {
                    accuracy: 65,
                    avgTime: 1200,
                    commonMistake: "Letter Reversal (b/d, p/q)",
                    recommendation: "Use highlighted letters, phonics-based games, and short reading chunks.",
                };
                break;
            case 'dyscalculia-risk':
                basePatterns.math = {
                    accuracy: 60,
                    avgTime: 1100,
                    commonMistake: "Number Reversal, Calculation Errors",
                    recommendation: "Use visual aids, manipulatives, and step-by-step problem solving.",
                };
                break;
            case 'attention-risk':
                basePatterns.focus = {
                    accuracy: 55,
                    avgTime: 600,
                    commonMistake: "Impulsive clicks, Sequence errors",
                    recommendation: "Short tasks with clear visual cues and structured breaks are helpful.",
                };
                break;
        }

        return basePatterns;
    };

    const studentData = generateDashboardData();

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
        if (!hasResults) {
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

    return (
        <div className="dashboard-container">
            {/* Header Section */}
            <header className="dashboard-header">
                <div className="header-content">
                    <h1 className="dashboard-title">Learning Assessment Dashboard</h1>
                    <p className="dashboard-subtitle">
                        {hasResults ? 'Your screening results & personalized recommendations' : 'Demo view - Complete an assessment for real results'}
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
            {!hasResults && (
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
                <div className="stat-card">
                    <div className="stat-icon">📅</div>
                    <div className="stat-content">
                        <span className="stat-label">Assessment Date</span>
                        <span className="stat-value">{studentData.assessmentDate}</span>
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

            {/* Main Content Grid */}
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

                        {studentData.keyInsights && studentData.keyInsights.length > 0 && (
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
