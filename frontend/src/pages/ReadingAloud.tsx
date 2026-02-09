import React, { useState, useEffect } from 'react';
import AudioRecorder from '../components/AudioRecorder';
import Mascot from '../components/Mascot';
import { getReadingSentence, submitAudioRecording } from '../services/api';
import type { AudioAnalysisResult } from '../types/types';
import '../styles/reading-aloud.css';

type ReadingPhase = 'instructions' | 'recording' | 'analyzing' | 'results';

interface ReadingAloudProps {
  userId: number;
  sessionId: string;
  ageGroup: string;
  onComplete: (results: AudioAnalysisResult | null) => void;
}

const ReadingAloud: React.FC<ReadingAloudProps> = ({
  userId,
  sessionId,
  ageGroup,
  onComplete
}) => {
  const [phase, setPhase] = useState<ReadingPhase>('instructions');
  const [sentence, setSentence] = useState<{ sentence_id: string; text: string; difficulty: string; domain: string } | null>(null);
  const [results, setResults] = useState<AudioAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Load sentence when entering recording phase
  useEffect(() => {
    if (phase === 'recording' && !sentence) {
      loadSentence();
    }
  }, [phase]);

  const loadSentence = async () => {
    try {
      const sentenceData = await getReadingSentence(userId, sessionId, ageGroup);
      setSentence(sentenceData);
    } catch (err) {
      setError('Failed to load reading sentence. Please try again.');
    }
  };

  const handleStartRecording = () => {
    setPhase('recording');
  };

  const handleSubmitRecording = async (audioBlob: Blob) => {
    if (!sentence) return;

    setIsSubmitting(true);
    setPhase('analyzing');
    setError(null);

    try {
      const analysisResults = await submitAudioRecording(
        audioBlob,
        userId,
        sessionId,
        sentence.text,
        ageGroup
      );
      setResults(analysisResults);
      setPhase('results');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze recording');
      setPhase('recording');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleComplete = () => {
    onComplete(results);
  };

  const handleSkip = () => {
    onComplete(null);
  };

  const handleRetry = () => {
    setResults(null);
    setError(null);
    setPhase('recording');
  };

  // Render instructions phase
  const renderInstructions = () => (
    <div className="reading-instructions smooth-fade-in">
      <div className="instructions-card glass-panel">
        <div className="mascot-wrapper">
          <Mascot expression="happy" size="large" />
        </div>

        <h1 className="instructions-title">
          <span className="gradient-text">Reading Time!</span>
        </h1>

        <p className="instructions-desc">
          Now let's hear you read! You'll see a sentence on the screen. 
          Read it aloud clearly into your microphone.
        </p>

        <div className="instructions-list">
          <div className="instruction-item">
            <span className="instruction-icon">🎤</span>
            <span>Click "Start Recording" when ready</span>
          </div>
          <div className="instruction-item">
            <span className="instruction-icon">📖</span>
            <span>Read the sentence clearly</span>
          </div>
          <div className="instruction-item">
            <span className="instruction-icon">⏱️</span>
            <span>Recording stops automatically after 8 seconds</span>
          </div>
          <div className="instruction-item">
            <span className="instruction-icon">🔄</span>
            <span>You can retake if needed</span>
          </div>
        </div>

        <div className="instructions-actions">
          <button className="hero-start-btn" onClick={handleStartRecording}>
            <span className="btn-text">Begin Reading Assessment</span>
            <span className="btn-icon">➜</span>
          </button>
          <button className="skip-btn" onClick={handleSkip}>
            Skip this step
          </button>
        </div>
      </div>

      {/* Ambient Background Elements */}
      <div className="ambient-orb orb-1"></div>
      <div className="ambient-orb orb-2"></div>
    </div>
  );

  // Render recording phase
  const renderRecording = () => (
    <div className="reading-recording smooth-fade-in">
      {error && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {sentence ? (
        <AudioRecorder
          sentence={sentence.text}
          maxDuration={8}
          onSubmit={handleSubmitRecording}
          isSubmitting={isSubmitting}
        />
      ) : (
        <div className="loading-sentence">
          <div className="loading-spinner"></div>
          <p>Loading sentence...</p>
        </div>
      )}
    </div>
  );

  // Render analyzing phase
  const renderAnalyzing = () => (
    <div className="reading-analyzing smooth-fade-in">
      <div className="analyzing-card glass-panel">
        <div className="analyzing-animation">
          <div className="analyzing-circle"></div>
          <div className="analyzing-circle delay-1"></div>
          <div className="analyzing-circle delay-2"></div>
        </div>
        <h2>Analyzing Your Reading...</h2>
        <p>Our AI is processing your recording. This may take a moment.</p>
      </div>
    </div>
  );

  // Render results phase
  const renderResults = () => {
    if (!results) return null;

    const { analysis } = results;
    const isHighRisk = analysis.risk_flag;

    return (
      <div className="reading-results smooth-fade-in">
        <div className="results-card glass-panel">
          <div className="results-header">
            <span className="results-icon">{isHighRisk ? '📊' : '🎉'}</span>
            <h1>Reading Analysis Complete</h1>
          </div>

          <div className="results-metrics">
            <div className="metric-card">
              <span className="metric-value">{analysis.accuracy_score}%</span>
              <span className="metric-label">Accuracy</span>
            </div>
            <div className="metric-card">
              <span className="metric-value">{analysis.reading_speed_wpm}</span>
              <span className="metric-label">Words/Min</span>
            </div>
          </div>

          {analysis.struggle_words && analysis.struggle_words.length > 0 && (
            <div className="struggle-words">
              <h3>Words to Practice</h3>
              <div className="word-chips">
                {analysis.struggle_words.map((word, index) => (
                  <span key={index} className="word-chip">{word}</span>
                ))}
              </div>
            </div>
          )}

          <div className="analysis-summary">
            <h3>Summary</h3>
            <p>{analysis.assessment_summary}</p>
          </div>

          {analysis.recommended_solution && (
            <div className="recommendation">
              <h3>💡 Recommendation</h3>
              <p>{analysis.recommended_solution}</p>
            </div>
          )}

          <div className="results-actions">
            <button className="primary-btn" onClick={handleComplete}>
              Continue to Results
              <span className="btn-arrow">→</span>
            </button>
            <button className="secondary-btn" onClick={handleRetry}>
              🔄 Try Again
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="reading-aloud-page assessment-page">
      {phase === 'instructions' && renderInstructions()}
      {phase === 'recording' && renderRecording()}
      {phase === 'analyzing' && renderAnalyzing()}
      {phase === 'results' && renderResults()}
    </div>
  );
};

export default ReadingAloud;
