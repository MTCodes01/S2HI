// API Types for LD Screening Assessment

// Session Types
export interface SessionResponse {
  user_id: number;
  session_id: string;
}

// Question Types
export interface Question {
  question_id: string;
  domain: 'reading' | 'writing' | 'math' | 'attention';
  difficulty: 'easy' | 'medium' | 'hard';
  question_text: string;
  options: string[];
  end_session?: boolean;
  message?: string;
}

// Answer Submission Types
export interface AnswerSubmission {
  user_id: number;
  session_id: string;
  question_id: string;
  domain: string;
  difficulty: string;
  correct: boolean;
  response_time_ms: number;
  confidence?: 'low' | 'medium' | 'high';
  mistake_type?: string;
}

export interface AnswerResponse {
  status: string;
  response_id: number;
}

// Session Result Types
export interface AssessmentResult {
  risk: 'low-risk' | 'dyslexia-risk' | 'dyscalculia-risk' | 'attention-risk';
  confidence_level: 'low' | 'moderate' | 'high';
  key_insights: string[];
}

// Domain Pattern for Dashboard
export interface DomainPattern {
  accuracy: number;
  avgTime: number;
  commonMistake: string;
  recommendation: string;
}

// Full Dashboard Data
export interface DashboardData {
  studentId: string;
  ageGroup: string;
  finalRisk: string;
  confidence: string;
  riskLevel: number;
  assessmentDate: string;
  summary: string;
  patterns: Record<string, DomainPattern>;
}

// Assessment State
export interface AssessmentState {
  userId: number | null;
  sessionId: string | null;
  currentQuestion: Question | null;
  questionNumber: number;
  isLoading: boolean;
  isComplete: boolean;
  results: AssessmentResult | null;
  error: string | null;
}

// Mistake Types
export type MistakeType = 
  | 'letter_reversal'
  | 'number_reversal'
  | 'spelling_error'
  | 'calculation_error'
  | 'sequence_error'
  | 'omission'
  | 'substitution';
