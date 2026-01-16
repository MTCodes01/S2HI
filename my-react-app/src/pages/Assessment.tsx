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

// New Games
import WordChainBuilder from '../games/WordChainBuilder';
import TimeEstimator from '../games/TimeEstimator';
import TaskSwitchSprint from '../games/TaskSwitchSprint';
import PlanAheadPuzzle from '../games/PlanAheadPuzzle';
import ConfidenceSlider from '../games/ConfidenceSlider';

type AssessmentPhase = 'welcome' | 'question' | 'loading' | 'confidence' | 'complete' | 'error';

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
    const [confidenceScore, setConfidenceScore] = useState<number>(50);

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
            // Check for existing user ID
            const storedUserId = localStorage.getItem('s2hi_user_id');
            const existingId = storedUserId ? parseInt(storedUserId) : undefined;

            const session = await startSession(ageGroup, existingId);
            setUserId(session.user_id);
            setSessionId(session.session_id);

            // Persist user ID
            localStorage.setItem('s2hi_user_id', session.user_id.toString());

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
                // Go to confidence check before ending
                setPhase('confidence');
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

    const handleConfidenceSubmit = async () => {
        if (!userId || !sessionId) return;
        setPhase('loading');
        try {
            // Map score to type
            let confLevel: "low" | "moderate" | "high" = "moderate";
            if (confidenceScore < 35) confLevel = "low";
            else if (confidenceScore > 75) confLevel = "high";

            const sessionResults = await endSession(userId, sessionId, confLevel);

            setResults({ ...sessionResults, confidence_level: confLevel });
            setPhase('complete');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to finalize session');
            setPhase('error');
        }
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
        <div className="assessment-welcome smooth-fade-in">
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

    // Render logic for games
    const renderGameComponent = () => {
        if (!currentQuestion) return null;

        const { domain, difficulty, question_text, options } = currentQuestion;

        // --- ATTENTION GAMES ---
        if (domain === 'attention') {
            if (difficulty === 'easy') {
                return (
                    <FocusGuard
                        stimulus={Math.random() > 0.3 ? "green" : "red"}
                        onAnswer={handleGameAnswer}
                        ageGroup={ageGroup}
                    />
                );
            } else if (difficulty === 'medium') {
                return (
                    <TaskSwitchSprint
                        initialRule="COLOR"
                        items={[
                            { shape: 'circle', color: 'blue' },
                            { shape: 'square', color: 'orange' },
                            { shape: 'circle', color: 'orange' },
                            { shape: 'square', color: 'blue' }
                        ]}
                        onAnswer={handleGameAnswer}
                        ageGroup={ageGroup}
                    />
                );
            } else {
                return (
                    <PatternWatcher
                        expectedPattern={["A", "B", "A", "B"]}
                        currentItem={Math.random() > 0.2 ? "A" : "C"}
                        isBreak={false}
                        onAnswer={handleGameAnswer}
                        ageGroup={ageGroup}
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
                        ageGroup={ageGroup}
                    />
                );
            } else if (difficulty === 'medium') {
                return (
                    <TimeEstimator
                        targetSeconds={5}
                        onAnswer={handleGameAnswer}
                        ageGroup={ageGroup}
                    />
                );
            } else {
                return (
                    <VisualMathMatch
                        equation={question_text}
                        correctValue={5}
                        options={[4, 5, 6]}
                        onAnswer={handleGameAnswer}
                        ageGroup={ageGroup}
                    />
                );
            }
        }

        // --- READING GAMES ---
        if (domain === 'reading') {
            if (difficulty === 'easy') {
                return (
                    <LetterFlipFrenzy
                        question={question_text}
                        options={options}
                        onAnswer={handleGameAnswer}
                        ageGroup={ageGroup}
                    />
                );
            } else if (difficulty === 'medium') {
                const target = currentQuestion.correct_option || "READ";
                const shuffled = target.toUpperCase().split('').sort(() => Math.random() - 0.5);
                return (
                    <WordChainBuilder
                        targetWord={target}
                        scrambledLetters={shuffled}
                        onAnswer={handleGameAnswer}
                        ageGroup={ageGroup}
                    />
                );
            } else {
                return (
                    <ReadAloudEcho
                        sentence={question_text}
                        onAnswer={handleGameAnswer}
                        ageGroup={ageGroup}
                    />
                );
            }
        }

        // --- LOGIC / EXECUTIVE FUNCTION ---
        if (domain === 'writing' || domain === 'logic') {
            return (
                <PlanAheadPuzzle
                    level={1}
                    onAnswer={handleGameAnswer}
                    ageGroup={ageGroup}
                />
            );
        }

        // Fallback
        return (
            <div className="p-8 text-center">
                <h2>{question_text}</h2>
                <div className="grid gap-4 mt-4">
                    {options.map((opt) => (
                        <button
                            key={opt}
                            onClick={() => handleGameAnswer({ correct: true })}
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

    const renderLoading = () => (
        <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading...</p>
        </div>
    );

    const renderConfidence = () => (
        <div className="confidence-screen-container smooth-fade-in">
            <div className="active-card glass-panel" style={{ maxWidth: '600px', margin: '0 auto', textAlign: 'center' }}>
                <h2 className="text-2xl font-bold mb-6 gradient-text">How did you feel?</h2>
                <p className="mb-8 text-gray-600">
                    Use the slider to show how confident you felt during the games.
                </p>

                <div className="py-8">
                    <ConfidenceSlider
                        value={confidenceScore}
                        onChange={setConfidenceScore}
                    />
                </div>

                <button
                    className="hero-start-btn mt-8"
                    onClick={handleConfidenceSubmit}
                    style={{ margin: '2rem auto' }}
                >
                    <span className="btn-text">Check My Results</span>
                    <span className="btn-icon">➜</span>
                </button>
            </div>
        </div>
    );

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
            {phase === 'confidence' && renderConfidence()}
            {phase === 'complete' && renderComplete()}
            {phase === 'error' && renderError()}
        </div>
    );
};

export default Assessment;
