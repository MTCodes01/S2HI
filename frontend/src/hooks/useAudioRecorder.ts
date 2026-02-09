import { useState, useRef, useCallback, useEffect } from 'react';
import type { AudioRecordingState, RecordingStatus } from '../types/types';

interface UseAudioRecorderOptions {
  maxDuration?: number; // Maximum recording duration in seconds
  onRecordingComplete?: (blob: Blob) => void;
}

interface UseAudioRecorderReturn extends AudioRecordingState {
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  reset: () => void;
  isSupported: boolean;
}

/**
 * Custom hook for audio recording using the MediaRecorder API.
 * Handles browser permissions, auto-stop timer, and proper cleanup.
 */
export function useAudioRecorder(options: UseAudioRecorderOptions = {}): UseAudioRecorderReturn {
  const { maxDuration = 8, onRecordingComplete } = options;

  const [status, setStatus] = useState<RecordingStatus>('idle');
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [recordingTime, setRecordingTime] = useState(0);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<number | null>(null);
  const autoStopRef = useRef<number | null>(null);

  // Check if MediaRecorder is supported
  const isSupported = typeof MediaRecorder !== 'undefined' && 
    typeof navigator.mediaDevices !== 'undefined' &&
    typeof navigator.mediaDevices.getUserMedia !== 'undefined';

  // Cleanup function
  const cleanup = useCallback(() => {
    // Stop timer
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    // Clear auto-stop timeout
    if (autoStopRef.current) {
      clearTimeout(autoStopRef.current);
      autoStopRef.current = null;
    }

    // Stop media recorder
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    mediaRecorderRef.current = null;

    // Stop all tracks on the stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      cleanup();
      // Revoke object URL to prevent memory leaks
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [cleanup, audioUrl]);

  const startRecording = useCallback(async () => {
    if (!isSupported) {
      setError('Audio recording is not supported in this browser.');
      setStatus('error');
      return;
    }

    // Reset previous recording
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
    }
    setAudioBlob(null);
    setAudioUrl(null);
    setError(null);
    chunksRef.current = [];
    setRecordingTime(0);
    setStatus('requesting');

    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      });
      streamRef.current = stream;

      // Determine best supported MIME type
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : MediaRecorder.isTypeSupported('audio/webm')
        ? 'audio/webm'
        : MediaRecorder.isTypeSupported('audio/mp4')
        ? 'audio/mp4'
        : 'audio/wav';

      const mediaRecorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: mimeType });
        const url = URL.createObjectURL(blob);
        setAudioBlob(blob);
        setAudioUrl(url);
        setStatus('stopped');

        // Call callback if provided
        if (onRecordingComplete) {
          onRecordingComplete(blob);
        }

        // Clean up the stream
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
          streamRef.current = null;
        }
      };

      mediaRecorder.onerror = () => {
        setError('Recording error occurred.');
        setStatus('error');
        cleanup();
      };

      // Start recording
      mediaRecorder.start(100); // Collect data every 100ms
      setStatus('recording');

      // Start recording timer
      timerRef.current = window.setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

      // Auto-stop after maxDuration
      autoStopRef.current = window.setTimeout(() => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
          mediaRecorderRef.current.stop();
          if (timerRef.current) {
            clearInterval(timerRef.current);
            timerRef.current = null;
          }
        }
      }, maxDuration * 1000);

    } catch (err) {
      // Handle specific permission errors
      if (err instanceof Error) {
        if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
          setError('Microphone access was denied. Please allow microphone access and try again.');
        } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
          setError('No microphone found. Please connect a microphone and try again.');
        } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
          setError('Microphone is already in use by another application.');
        } else {
          setError(`Failed to access microphone: ${err.message}`);
        }
      } else {
        setError('An unknown error occurred while accessing the microphone.');
      }
      setStatus('error');
      cleanup();
    }
  }, [isSupported, maxDuration, audioUrl, cleanup, onRecordingComplete]);

  const stopRecording = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    if (autoStopRef.current) {
      clearTimeout(autoStopRef.current);
      autoStopRef.current = null;
    }
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
  }, []);

  const reset = useCallback(() => {
    cleanup();
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
    }
    setStatus('idle');
    setAudioBlob(null);
    setAudioUrl(null);
    setError(null);
    setRecordingTime(0);
    chunksRef.current = [];
  }, [cleanup, audioUrl]);

  return {
    status,
    audioBlob,
    audioUrl,
    error,
    recordingTime,
    startRecording,
    stopRecording,
    reset,
    isSupported
  };
}

export default useAudioRecorder;
