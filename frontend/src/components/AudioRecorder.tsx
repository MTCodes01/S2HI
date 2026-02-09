import React, { useEffect, useRef } from 'react';
import { useAudioRecorder } from '../hooks/useAudioRecorder';
import type { RecordingStatus } from '../types/types';
import '../styles/reading-aloud.css';

interface AudioRecorderProps {
  sentence: string;
  maxDuration?: number;
  onSubmit: (audioBlob: Blob) => void;
  isSubmitting?: boolean;
}

/**
 * Audio recorder component with visual feedback, playback, and retake functionality.
 */
const AudioRecorder: React.FC<AudioRecorderProps> = ({
  sentence,
  maxDuration = 8,
  onSubmit,
  isSubmitting = false
}) => {
  const {
    status,
    audioBlob,
    audioUrl,
    error,
    recordingTime,
    startRecording,
    stopRecording,
    reset,
    isSupported
  } = useAudioRecorder({ maxDuration });

  const audioRef = useRef<HTMLAudioElement>(null);

  // Format time as MM:SS
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Handle submit click
  const handleSubmit = () => {
    if (audioBlob) {
      onSubmit(audioBlob);
    }
  };

  // Play audio
  const handlePlay = () => {
    if (audioRef.current) {
      audioRef.current.play();
    }
  };

  // Stop/pause audio
  const handlePause = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
  };

  // Cleanup audio on unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
      }
    };
  }, []);

  if (!isSupported) {
    return (
      <div className="audio-recorder-error">
        <div className="error-icon">🎤</div>
        <h3>Audio Recording Not Supported</h3>
        <p>Your browser does not support audio recording. Please try using Chrome, Firefox, or Edge.</p>
      </div>
    );
  }

  const renderRecordingIndicator = () => (
    <div className="recording-indicator">
      <div className="recording-pulse"></div>
      <span className="recording-text">Recording...</span>
      <div className="recording-timer">
        <span className="time-elapsed">{formatTime(recordingTime)}</span>
        <span className="time-separator">/</span>
        <span className="time-remaining">{formatTime(maxDuration)}</span>
      </div>
      <div className="recording-progress">
        <div 
          className="recording-progress-bar" 
          style={{ width: `${(recordingTime / maxDuration) * 100}%` }}
        ></div>
      </div>
    </div>
  );

  const renderStatusIndicator = (currentStatus: RecordingStatus) => {
    switch (currentStatus) {
      case 'requesting':
        return (
          <div className="status-indicator requesting">
            <div className="loading-spinner-small"></div>
            <span>Requesting microphone access...</span>
          </div>
        );
      case 'recording':
        return renderRecordingIndicator();
      case 'stopped':
        return (
          <div className="status-indicator stopped">
            <span className="success-icon">✓</span>
            <span>Recording complete ({formatTime(recordingTime)})</span>
          </div>
        );
      case 'error':
        return (
          <div className="status-indicator error">
            <span className="error-icon-small">⚠️</span>
            <span>{error}</span>
          </div>
        );
      default:
        return (
          <div className="status-indicator idle">
            <span className="mic-icon">🎤</span>
            <span>Click "Start Recording" when ready</span>
          </div>
        );
    }
  };

  return (
    <div className="audio-recorder">
      {/* Sentence to read */}
      <div className="sentence-card">
        <h3 className="sentence-label">Read this sentence aloud:</h3>
        <p className="sentence-text">{sentence}</p>
      </div>

      {/* Status and recording indicator */}
      <div className="recorder-status">
        {renderStatusIndicator(status)}
      </div>

      {/* Hidden audio element for playback */}
      {audioUrl && (
        <audio ref={audioRef} src={audioUrl} preload="auto" />
      )}

      {/* Controls */}
      <div className="recorder-controls">
        {status === 'idle' && (
          <button 
            className="record-btn start"
            onClick={startRecording}
            disabled={isSubmitting}
          >
            <span className="btn-icon">🎙️</span>
            <span>Start Recording</span>
          </button>
        )}

        {status === 'requesting' && (
          <button className="record-btn disabled" disabled>
            <span className="btn-icon">⏳</span>
            <span>Waiting for permission...</span>
          </button>
        )}

        {status === 'recording' && (
          <button 
            className="record-btn stop"
            onClick={stopRecording}
          >
            <span className="btn-icon">⏹️</span>
            <span>Stop Recording</span>
          </button>
        )}

        {status === 'stopped' && audioUrl && (
          <div className="playback-controls">
            <button 
              className="control-btn play"
              onClick={handlePlay}
              disabled={isSubmitting}
            >
              <span className="btn-icon">▶️</span>
              <span>Play</span>
            </button>
            <button 
              className="control-btn pause"
              onClick={handlePause}
              disabled={isSubmitting}
            >
              <span className="btn-icon">⏸️</span>
              <span>Pause</span>
            </button>
            <button 
              className="control-btn retake"
              onClick={reset}
              disabled={isSubmitting}
            >
              <span className="btn-icon">🔄</span>
              <span>Retake</span>
            </button>
          </div>
        )}

        {status === 'error' && (
          <button 
            className="record-btn retry"
            onClick={reset}
          >
            <span className="btn-icon">🔄</span>
            <span>Try Again</span>
          </button>
        )}
      </div>

      {/* Submit button - only show when recording is complete */}
      {status === 'stopped' && audioBlob && (
        <button 
          className="submit-recording-btn"
          onClick={handleSubmit}
          disabled={isSubmitting}
        >
          {isSubmitting ? (
            <>
              <div className="loading-spinner-small"></div>
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <span>Submit Recording</span>
              <span className="btn-arrow">→</span>
            </>
          )}
        </button>
      )}
    </div>
  );
};

export default AudioRecorder;
