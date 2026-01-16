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
export async function startSession(ageGroup: string): Promise<SessionResponse> {
  return apiRequest<SessionResponse>('/start-session/', { age_group: ageGroup });
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
  sessionId: string
): Promise<AssessmentResult> {
  return apiRequest<AssessmentResult>('/end-session/', {
    user_id: userId,
    session_id: sessionId
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


