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
  correct_option?: string;
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

export type MistakeType =
  | 'letter_reversal'
  | 'number_reversal'
  | 'spelling_error'
  | 'calculation_error'
  | 'sequence_error'
  | 'omission'
  | 'substitution';

// Dashboard API Types
export interface DashboardDataRequest {
  user_id: number;
  session_id: string;
}

export interface DomainPerformance {
  accuracy: number;
  avg_time: number;
  common_mistake: string;
  recommendation: string;
}

export interface DashboardDataResponse {
  student_id: string;
  age_group: string;
  final_risk: string;
  confidence: string;
  risk_level: number;
  assessment_date: string;
  summary: string;
  key_insights: string[];
  patterns: {
    reading: DomainPerformance;
    math: DomainPerformance;
    focus: DomainPerformance;
  };
}

// Audio Recording Types
export type RecordingStatus = 'idle' | 'requesting' | 'recording' | 'stopped' | 'error';

export interface AudioRecordingState {
  status: RecordingStatus;
  audioBlob: Blob | null;
  audioUrl: string | null;
  error: string | null;
  recordingTime: number;
}

export interface ReadingSentence {
  sentence_id: string;
  text: string;
  difficulty: 'easy' | 'medium' | 'hard';
  domain: string;
}

export interface AudioAnalysisResult {
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
}

// Assessment Stage Types
export type AssessmentStage = 'questions' | 'reading' | 'complete';

export interface FullAssessmentState {
  stage: AssessmentStage;
  userId: number | null;
  sessionId: string | null;
  ageGroup: string;
  questionResults: AssessmentResult | null;
  readingResults: AudioAnalysisResult | null;
}
