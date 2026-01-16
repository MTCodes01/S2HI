import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { startSession, getNextQuestion, submitAnswer, endSession } from '../services/api';
import type { Question, AssessmentResult } from '../types/types';
import Mascot from '../components/Mascot';
import '../styles/assessment.css';

// Game Imports
import FocusGuard from '../games/FocusGuard';
import PatternWatcher from '../games/PatternWatcher';
import LetterFlipFrenzy from '../games/LetterFlipFrenzy';
import ReadAloudEcho from '../games/ReadAloudEcho';
import NumberSenseDash from '../games/NumberSenseDash';
import VisualMathMatch from '../games/VisualMathMatch';

type AssessmentPhase = 'welcome' | 'question' | 'loading' | 'complete' | 'error';

const Assessment: React.FC = () => {
    const navigate = useNavigate();

    // Session state
    const [userId, setUserId] = useState<number | null>(null);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [ageGroup, setAgeGroup] = useState<string>('9-11');

    // Question state
    const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
    const [questionNumber, setQuestionNumber] = useState(0);

    // UI state
    const [phase, setPhase] = useState<AssessmentPhase>('welcome');
    const [error, setError] = useState<string | null>(null);
    const [results, setResults] = useState<AssessmentResult | null>(null);

    // Timer ref
    const startTimeRef = useRef<number>(0);

    const ageGroups = [
        { value: '6-8', label: '6-8 years' },
        { value: '9-11', label: '9-11 years' },
        { value: '12-14', label: '12-14 years' },
    ];

    // Start a new session
    const handleStartSession = async () => {
        setPhase('loading');
        setError(null);

        try {
            const session = await startSession(ageGroup);
            setUserId(session.user_id);
            setSessionId(session.session_id);

            // Get first question
            const question = await getNextQuestion(session.user_id, session.session_id);

            if (question.end_session) {
                setPhase('complete');
                return;
            }

            setCurrentQuestion(question);
            setQuestionNumber(1);
            startTimeRef.current = Date.now();
            setPhase('question');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to start session');
            setPhase('error');
        }
    };

    // Generic handler for all games to submit their results
    const handleGameAnswer = async (result: any) => {
        if (!currentQuestion || !userId || !sessionId) return;

        setPhase('loading');

        // Normalize result types from different games
        const isCorrect = result.correct !== undefined ? result.correct : (result.accuracy > 0.8);
        const responseTime = result.responseTime || (Date.now() - startTimeRef.current);
        const mistakeType = result.mistakeType || (isCorrect ? undefined : "general_error");

        try {
            // Submit the answer
            await submitAnswer({
                user_id: userId,
                session_id: sessionId,
                question_id: currentQuestion.question_id,
                domain: currentQuestion.domain,
                difficulty: currentQuestion.difficulty,
                correct: isCorrect,
                response_time_ms: responseTime,
                confidence: 'medium',
                mistake_type: mistakeType
            });

            // Get next question
            const nextQuestion = await getNextQuestion(userId, sessionId, {
                id: currentQuestion.question_id,
                correct: isCorrect,
                responseTime: responseTime
            });

            if (nextQuestion.end_session) {
                // End session and get results
                const sessionResults = await endSession(userId, sessionId);
                setResults(sessionResults);
                setPhase('complete');
            } else {
                setCurrentQuestion(nextQuestion);
                setQuestionNumber(prev => prev + 1);
                startTimeRef.current = Date.now();
                setPhase('question');
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to submit answer');
            setPhase('error');
        }
    };

    // Navigate to dashboard with results
    const handleViewResults = () => {
        navigate('/dashboard', {
            state: {
                results,
                userId,
                sessionId,
                ageGroup
            }
        });
    };

    // Restart assessment
    const handleRestart = () => {
        setUserId(null);
        setSessionId(null);
        setCurrentQuestion(null);
        setQuestionNumber(0);
        setResults(null);
        setError(null);
        setPhase('welcome');
    };

    // Render welcome screen
    const renderWelcome = () => (
        <div className={`assessment-welcome smooth-fade-in`}>
            <div className="welcome-card glass-panel">
                <div className="mascot-wrapper">
                    <Mascot expression="happy" size="large" />
                </div>

                <h1 className="welcome-title">
                    <span className="gradient-text">Ready to Learn?</span>
                </h1>
                <p className="welcome-desc">
                    Let's discover your unique superpowers!
                    Select your age to begin your personal adventure.
                </p>

                <div className="age-selection-container">
                    <div className="age-options-grid">
                        {ageGroups.map(group => (
                            <button
                                key={group.value}
                                className={`age-card-btn ${ageGroup === group.value ? 'selected' : ''}`}
                                onClick={() => setAgeGroup(group.value)}
                            >
                                <div className="age-card-content">
                                    <span className="age-card-label">{group.value}</span>
                                    <span className="age-card-sub">Years</span>
                                </div>
                                {ageGroup === group.value && <div className="selected-check">✓</div>}
                            </button>
                        ))}
                    </div>
                </div>

                <button className="hero-start-btn" onClick={handleStartSession}>
                    <span className="btn-text">Start Assessment</span>
                    <span className="btn-icon">➜</span>
                </button>

                <div className="features-row">
                    <div className="feature-pill">
                        <span className="feature-icon">⚡</span> 5 Mins
                    </div>
                    <div className="feature-pill">
                        <span className="feature-icon">🎮</span> Fun
                    </div>
                    <div className="feature-pill">
                        <span className="feature-icon">🛡️</span> Private
                    </div>
                </div>
            </div>

            <div className="ambient-orb orb-1"></div>
            <div className="ambient-orb orb-2"></div>
        </div>
    );

    // Render the specific game component based on question domain/type
    const renderGameComponent = () => {
        if (!currentQuestion) return null;

        const { domain, difficulty, question_text, options } = currentQuestion;

        // --- ATTENTION GAMES ---
        if (domain === 'attention') {
            if (difficulty === 'easy' || difficulty === 'medium') {
                return (
                    <FocusGuard
                        stimulus={Math.random() > 0.3 ? "green" : "red"} // Randomize stimulus for demo
                        onAnswer={handleGameAnswer}
                    />
                );
            } else {
                return (
                    <PatternWatcher
                        expectedPattern={["A", "B", "A", "B"]}
                        currentItem={Math.random() > 0.2 ? "A" : "C"} // Demo logic
                        isBreak={false} // Would need real game state logic here
                        onAnswer={handleGameAnswer}
                    />
                );
            }
        }

        // --- MATH GAMES ---
        if (domain === 'math') {
            if (difficulty === 'easy') {
                return (
                    <NumberSenseDash
                        left={Math.floor(Math.random() * 20)}
                        right={Math.floor(Math.random() * 20)}
                        onAnswer={handleGameAnswer}
                    />
                );
            } else {
                return (
                    <VisualMathMatch
                        equation={question_text}
                        correctValue={5} // Placeholder - should parse from question
                        options={[4, 5, 6]} // Placeholder
                        onAnswer={handleGameAnswer}
                    />
                );
            }
        }

        // --- READING GAMES ---
        if (domain === 'reading') {
            if (difficulty === 'hard') {
                return (
                    <ReadAloudEcho
                        sentence={question_text}
                        onAnswer={handleGameAnswer}
                    />
                );
            } else {
                return (
                    <LetterFlipFrenzy
                        question={question_text}
                        options={options}
                        onAnswer={handleGameAnswer}
                    />
                );
            }
        }

        // Fallback or Writing
        return (
            <div className="p-8 text-center">
                <h2>{question_text}</h2>
                <div className="grid gap-4 mt-4">
                    {options.map((opt) => (
                        <button
                            key={opt}
                            onClick={() => handleGameAnswer({ correct: true })} // Placeholder
                            className="p-4 border rounded hover:bg-gray-100"
                        >
                            {opt}
                        </button>
                    ))}
                </div>
            </div>
        );
    };

    // Render question container
    const renderQuestion = () => {
        if (!currentQuestion) return null;

        const domainColors: Record<string, string> = {
            reading: '#ff6b6b',
            writing: '#9b59b6',
            math: '#2ecc71',
            attention: '#ffc857'
        };

        return (
            <div className="question-container">
                <div className="question-header">
                    <div className="progress-info">
                        <span className="question-count">Question {questionNumber}</span>
                        <div
                            className="domain-badge"
                            style={{ backgroundColor: `${domainColors[currentQuestion.domain]}20`, color: domainColors[currentQuestion.domain] }}
                        >
                            {currentQuestion.domain}
                        </div>
                    </div>
                </div>

                <div className="question-card game-wrapper">
                    {renderGameComponent()}
                </div>
            </div>
        );
    };

    // Render loading
    const renderLoading = () => (
        <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading...</p>
        </div>
    );

    // Render complete
    const renderComplete = () => (
        <div className="complete-container">
            <div className="complete-card">
                <div className="complete-icon">🎉</div>
                <h1>Assessment Complete!</h1>
                <p>Great job! Your results are ready for review.</p>

                {results && (
                    <div className="results-preview">
                        <div className={`risk-indicator ${results.risk}`}>
                            <span className="risk-label">Risk Assessment</span>
                            <span className="risk-value">{results.risk.replace('-', ' ')}</span>
                        </div>
                        <div className="confidence-indicator">
                            <span>Confidence: </span>
                            <strong>{results.confidence_level}</strong>
                        </div>
                    </div>
                )}

                <div className="complete-actions">
                    <button className="view-results-btn" onClick={handleViewResults}>
                        📊 View Detailed Results
                    </button>
                    <button className="restart-btn" onClick={handleRestart}>
                        🔄 Take Another Assessment
                    </button>
                </div>
            </div>
        </div>
    );

    // Render error
    const renderError = () => (
        <div className="error-container">
            <div className="error-card">
                <div className="error-icon">⚠️</div>
                <h2>Something went wrong</h2>
                <p>{error}</p>
                <button className="retry-btn" onClick={handleRestart}>
                    Try Again
                </button>
            </div>
        </div>
    );

    return (
        <div className="assessment-page">
            {phase === 'welcome' && renderWelcome()}
            {phase === 'question' && renderQuestion()}
            {phase === 'loading' && renderLoading()}
            {phase === 'complete' && renderComplete()}
            {phase === 'error' && renderError()}
        </div>
    );
};

export default Assessment;
