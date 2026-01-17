"""
ML model integration utilities.
COMBINED VERSION: Handles Model Loading, Feature Extraction, Prediction, AND Gemini AI Reporting.
"""
import os
import numpy as np
import pandas as pd
from typing import Dict, List, Any
from django.conf import settings

# --- 1. NEW: Google GenAI Import ---
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False
    print("⚠️ Google GenAI library not found. Install with `pip install google-genai`")

# --- 2. EXISTING: Joblib Import ---
try:
    import joblib
    HAS_JOBLIB = True
except ImportError:
    HAS_JOBLIB = False

# Paths
QUESTION_MODEL_PATH = os.path.join(settings.BASE_DIR, 'question_generator.pkl')
PREDICTION_MODEL_PATH = os.path.join(settings.BASE_DIR, 'prediction_model.pkl')

# Global Instances
_question_model = None
_prediction_model = None
_gemini_client = None 

# ==========================================
# 🧠 NEW: GEMINI AI REPORTING ENGINE
# ==========================================
def get_gemini_client():
    """Initialize Gemini client safely."""
    global _gemini_client
    if _gemini_client is None and HAS_GENAI:
        try:
            api_key = getattr(settings, 'GEMINI_API_KEY', None)
            if api_key:
                _gemini_client = genai.Client(api_key=api_key)
        except Exception as e:
            print(f"⚠️ Gemini Client Setup Failed: {e}")
    return _gemini_client

def generate_ai_report_text(stats: Dict[str, Any], risk_label: str) -> str:
    """
    Asks Gemini to write a professional clinical summary based on the stats.
    """
    client = get_gemini_client()
    if not client:
        return "AI Summary unavailable (API Key missing or client error)."

    prompt = f"""
    Act as an Educational Psychologist. Write a concise, 2-sentence clinical summary for a teacher based on this student's assessment data:
    
    - Risk Profile: {risk_label}
    - Reading Accuracy: {int(stats.get('reading_acc', 0)*100)}%
    - Math Accuracy: {int(stats.get('math_acc', 0)*100)}%
    - Focus/Attention Score: {int(stats.get('focus_acc', 0)*100)}%
    - Response Speed: {int(stats.get('avg_time_ms', 0))}ms (Avg)
    - Reversal Rate: {int(stats.get('rev_rate', 0)*100)}% (Letter/Number confusion)
    - Impulsivity: {int(stats.get('impulse_rate', 0)*100)}% (Fast, wrong answers)

    If the risk is low, mention their strengths. If high, suggest a specific intervention.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[prompt],
            config=types.GenerateContentConfig(response_mime_type="text/plain")
        )
        return response.text.strip()
    except Exception as e:
        print(f"❌ Gemini Generation Error: {e}")
        return "AI Analysis could not be completed."

# ==========================================
# 📦 EXISTING: MODEL LOADERS
# ==========================================

def load_question_model():
    """Load the question generation ML model from disk."""
    global _question_model
    if _question_model is None:
        # Check current dir as well
        current_dir = os.path.dirname(os.path.abspath(__file__))
        paths = [QUESTION_MODEL_PATH, os.path.join(current_dir, 'question_model.pkl')]
        
        for path in paths:
            if HAS_JOBLIB and os.path.exists(path):
                try:
                    _question_model = joblib.load(path)
                    print(f"✅ Loaded question model from {path}")
                    break
                except: pass
        
        if _question_model is None:
            _question_model = PlaceholderQuestionModel()
            
    return _question_model

def load_prediction_model():
    """Load the final prediction ML model from disk."""
    global _prediction_model
    if _prediction_model is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        paths = [PREDICTION_MODEL_PATH, os.path.join(current_dir, 'risk_classifier.pkl')]

        for path in paths:
            if HAS_JOBLIB and os.path.exists(path):
                try:
                    _prediction_model = joblib.load(path)
                    print(f"✅ Loaded prediction model from {path}")
                    break
                except: pass

        if _prediction_model is None:
            _prediction_model = PlaceholderPredictionModel()
            
    return _prediction_model

# ==========================================
# 🧩 EXISTING: PLACEHOLDER MODELS
# ==========================================

class PlaceholderQuestionModel:
    def predict(self, features: np.ndarray) -> np.ndarray:
        # Logic: if correct & fast -> harder, else easier
        last_correct = features[0][0]
        last_time = features[0][1]
        current_domain = features[0][6]
        
        next_diff = 1 # Medium
        if last_correct and last_time < 1500: next_diff = 2
        elif not last_correct: next_diff = 0
        
        next_domain = (int(current_domain) + 1) % 3 
        return np.array([next_domain, next_diff])

class PlaceholderPredictionModel:
    def predict(self, features: np.ndarray) -> np.ndarray:
        return np.array(['Low Risk']) # Default fallback
    def predict_proba(self, features: np.ndarray) -> np.ndarray:
        return np.array([0.85]) 

# ==========================================
# 📊 EXISTING: FEATURE EXTRACTION (RESTORED)
# ==========================================

def extract_question_features(session_id, last_question_id=None, correct=None, response_time_ms=None):
    """
    Extract features for question generation model.
    RESTORED from your original code.
    """
    from .models import UserResponse, Question
    
    # Defaults
    if not last_question_id or correct is None or response_time_ms is None:
        return np.array([[1, 1000, 0, 1, 0, 1.0, 0]])
    
    # Get last question difficulty
    try:
        last_question = Question.objects.get(question_id=last_question_id)
        last_difficulty = last_question.difficulty
        last_domain = last_question.domain
    except Question.DoesNotExist:
        last_difficulty = 'medium'
        last_domain = 'reading'
    
    # One-hot encode difficulty
    diff_easy = 1 if last_difficulty == 'easy' else 0
    diff_medium = 1 if last_difficulty == 'medium' else 0
    diff_hard = 1 if last_difficulty == 'hard' else 0
    
    # Domain map
    domain_map = {'reading': 0, 'writing': 0, 'math': 1, 'attention': 2, 'focus': 2}
    cur_domain_val = domain_map.get(last_domain, 0)

    # Session Accuracy
    responses = UserResponse.objects.filter(session_id=session_id)
    if responses.exists():
        session_accuracy = responses.filter(correct=True).count() / responses.count()
    else:
        session_accuracy = 1.0

    return np.array([[
        1 if correct else 0,
        response_time_ms,
        diff_easy, diff_medium, diff_hard,
        session_accuracy,
        cur_domain_val
    ]])

# ==========================================
# 🔮 COMBINED: PREDICTION LOGIC
# ==========================================

def get_prediction(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Get risk prediction from ML model AND Gemini AI text report.
    """
    # 1. Initialize Result
    result = {
        'risk': 'low-risk',
        'confidence_level': 'low',
        'key_insights': [],
        'scores': {'dyslexia': 0.1, 'dyscalculia': 0.1, 'attention': 0.1}
    }

    if not responses:
        result['key_insights'].append("Insufficient data.")
        return result

    try:
        # 2. Calculate Stats
        total = len(responses)
        def get_acc(domain_list):
            subset = [r for r in responses if r.get('domain') in domain_list]
            if not subset: return 0.0
            return sum(1 for r in subset if r.get('correct')) / len(subset)

        reading_acc = get_acc(['reading', 'writing'])
        math_acc = get_acc(['math'])
        focus_acc = get_acc(['attention', 'focus'])
        avg_time = sum(r.get('response_time_ms', 0) for r in responses) / total
        
        rev_count = sum(1 for r in responses if r.get('mistake_type') in ['letter_reversal', 'number_reversal'])
        rev_rate = rev_count / total
        
        impulse_count = sum(1 for r in responses if not r.get('correct') and r.get('response_time_ms', 2000) < 1000)
        impulse_rate = impulse_count / total

        # 3. Get ML Prediction
        model = load_prediction_model()
        
        # Features for model
        features = pd.DataFrame([{
            "reading_acc": reading_acc, "math_acc": math_acc, "focus_acc": focus_acc,
            "avg_time_ms": avg_time, "rev_rate": rev_rate, "pv_rate": 0.0, "impulse_rate": impulse_rate
        }])
        
        try:
            prediction_label = model.predict(features)[0]
        except:
            # Fallback Logic
            if rev_rate > 0.25: prediction_label = 'Dyslexia Risk'
            elif impulse_rate > 0.35: prediction_label = 'Attention Risk'
            else: prediction_label = 'Low Risk'

        label_map = {'Low Risk': 'low-risk', 'Dyslexia Risk': 'dyslexia-risk', 'Dyscalculia Risk': 'dyscalculia-risk', 'Attention Risk': 'attention-risk'}
        final_risk = label_map.get(prediction_label, 'low-risk')
        result['risk'] = final_risk

        # 4. Generate AI Text Report
        print("🤖 Generating AI Text Report...")
        stats_for_ai = {
            'reading_acc': reading_acc, 'math_acc': math_acc, 'focus_acc': focus_acc,
            'avg_time_ms': avg_time, 'rev_rate': rev_rate, 'impulse_rate': impulse_rate
        }
        ai_summary = generate_ai_report_text(stats_for_ai, final_risk)
        result['key_insights'].append(ai_summary)

        # 5. Set Scores
        if 'dyslexia' in final_risk: result['scores']['dyslexia'] = 0.85
        elif 'dyscalculia' in final_risk: result['scores']['dyscalculia'] = 0.85
        elif 'attention' in final_risk: result['scores']['attention'] = 0.85
        
        result['confidence_level'] = 'high'

    except Exception as e:
        print(f"❌ Analysis Error: {e}")
        result['key_insights'].append("Error during analysis.")

    return result