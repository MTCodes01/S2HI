// API Service for LD Screening Backend
import type {
  SessionResponse,
  Question,
  AnswerSubmission,
  AnswerResponse,
  AssessmentResult,
  DashboardDataResponse
} from '../types/types';

const API_BASE_URL = 'http://localhost:8000';

// Helper function for API requests
async function apiRequest<T>(
  endpoint: string,
  data: Record<string, unknown>
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Network error' }));
    throw new Error(error.error || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Start a new assessment session
 * @param ageGroup - User's age group (e.g., "6-8", "9-11", "12-14")
 */
export async function startSession(ageGroup: string, userId?: number): Promise<SessionResponse> {
  return apiRequest<SessionResponse>('/start-session/', {
    age_group: ageGroup,
    user_id: userId
  });
}

/**
 * Get the next adaptive question
 * @param userId - User ID from session
 * @param sessionId - Session ID from session
 * @param lastQuestion - Optional previous question response info
 */
export async function getNextQuestion(
  userId: number,
  sessionId: string,
  lastQuestion?: {
    id: string;
    correct: boolean;
    responseTime: number;
  }
): Promise<Question> {
  const body: Record<string, unknown> = {
    user_id: userId,
    session_id: sessionId
  };

  if (lastQuestion) {
    body.last_question_id = lastQuestion.id;
    body.correct = lastQuestion.correct;
    body.response_time_ms = lastQuestion.responseTime;
  }

  return apiRequest<Question>('/get-next-question/', body);
}

/**
 * Submit an answer for the current question
 */
export async function submitAnswer(
  submission: AnswerSubmission
): Promise<AnswerResponse> {
  return apiRequest<AnswerResponse>('/submit-answer/', {
    user_id: submission.user_id,
    session_id: submission.session_id,
    question_id: submission.question_id,
    domain: submission.domain,
    difficulty: submission.difficulty,
    correct: submission.correct,
    response_time_ms: submission.response_time_ms,
    confidence: submission.confidence,
    mistake_type: submission.mistake_type
  });
}

/**
 * End the session and get ML prediction results
 */
export async function endSession(
  userId: number,
  sessionId: string,
  confidence?: string
): Promise<AssessmentResult> {
  return apiRequest<AssessmentResult>('/end-session/', {
    user_id: userId,
    session_id: sessionId,
    confidence_level: confidence
  });
}

/**
 * Get comprehensive dashboard data for a completed session
 */
export async function getDashboardData(
  userId: number,
  sessionId: string
): Promise<DashboardDataResponse> {
  return apiRequest<DashboardDataResponse>('/get-dashboard-data/', {
    user_id: userId,
    session_id: sessionId
  });
}

/**
 * Get user assessment history
 */
export async function getUserHistory(
  userId: number
): Promise<{
  date: string;
  time: string;
  datetime: string;
  session_id: string;
  dyslexia_score: number;
  dyscalculia_score: number;
  attention_score: number;
  risk_label: string;
}[]> {
  return apiRequest('/get-user-history/', { user_id: userId });
}

// Reading sentences for reading aloud assessment
const READING_SENTENCES = [
  { sentence_id: 'RS001', text: 'The quick brown fox jumps over the lazy dog.', difficulty: 'easy' as const, domain: 'reading' },
  { sentence_id: 'RS002', text: 'Sally sells seashells by the seashore on sunny summer days.', difficulty: 'medium' as const, domain: 'reading' },
  { sentence_id: 'RS003', text: 'Peter Piper picked a peck of pickled peppers.', difficulty: 'medium' as const, domain: 'reading' },
  { sentence_id: 'RS004', text: 'She sells fresh fish by the shore every morning.', difficulty: 'easy' as const, domain: 'reading' },
  { sentence_id: 'RS005', text: 'The butterfly fluttered between the beautiful bright flowers.', difficulty: 'hard' as const, domain: 'reading' },
];

/**
 * Get a reading sentence for the reading aloud assessment
 */
export async function getReadingSentence(
  _userId: number,
  _sessionId: string
): Promise<{ sentence_id: string; text: string; difficulty: string; domain: string }> {
  // For now, return a random sentence from the local list
  // In the future, this could be an API call to get personalized sentences
  const randomIndex = Math.floor(Math.random() * READING_SENTENCES.length);
  return Promise.resolve(READING_SENTENCES[randomIndex]);
}

/**
 * Submit audio recording for analysis
 */
export async function submitAudioRecording(
  audioBlob: Blob,
  userId: number | string,
  sessionId: string,
  expectedText: string,
  ageGroup: string
): Promise<{
  status: string;
  analysis: {
    transcribed_text?: string;
    accuracy_score: number;
    reading_speed_wpm: number;
    struggle_words: string[];
    assessment_summary: string;
    risk_flag: boolean;
    recommended_solution: string;
  };
}> {
  const formData = new FormData();
  
  // Determine file extension based on blob type
  const extension = audioBlob.type.includes('webm') ? 'webm' : 
                    audioBlob.type.includes('mp4') ? 'mp4' : 'wav';
  
  formData.append('audio', audioBlob, `recording.${extension}`);
  formData.append('user_id', String(userId));
  formData.append('session_id', sessionId);
  formData.append('expected_text', expectedText);
  formData.append('age_group', ageGroup);

  const response = await fetch(`${API_BASE_URL}/reading/analyze-reading/`, {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Network error' }));
    throw new Error(error.error || `HTTP ${response.status}`);
  }

  return response.json();
}
