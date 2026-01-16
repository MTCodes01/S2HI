"""
ML model integration utilities.
Handles model loading, feature extraction, and prediction.
"""
import os
import numpy as np
import pandas as pd
from typing import Dict, List, Any
from django.conf import settings

# Try to import joblib, fall back to placeholder if not available
try:
    import joblib
    HAS_JOBLIB = True
except ImportError:
    HAS_JOBLIB = False

# Paths to the ML models
QUESTION_MODEL_PATH = os.path.join(settings.BASE_DIR, 'question_generator.pkl')
PREDICTION_MODEL_PATH = os.path.join(settings.BASE_DIR, 'prediction_model.pkl')

# Global model instances
_question_model = None
_prediction_model = None


def load_question_model():
    """Load the question generation ML model from disk."""
    global _question_model
    if _question_model is None:
        import sys
        
        # Ensure the current directory is in sys.path so the unpickler can find 'question_generator_model'
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.append(current_dir)
            
        # Check multiple locations
        paths_to_check = [
            os.path.join(current_dir, 'question_model.pkl'),       # Trained script output
            os.path.join(settings.BASE_DIR, 'question_generator.pkl'), # Old location
        ]
        
        model_path = None
        for path in paths_to_check:
            if os.path.exists(path):
                model_path = path
                break
        
        if model_path:
            try:
                _question_model = joblib.load(model_path)
                print(f"✅ Loaded question generation model from {model_path}")
            except Exception as e:
                 print(f"❌ Failed to load question model from {model_path}: {e}")
        else:
             print("⚠️  No question generation model found.")

    return _question_model


def load_prediction_model():
    """Load the final prediction ML model from disk."""
    global _prediction_model
    if _prediction_model is None:
        if HAS_JOBLIB and os.path.exists(PREDICTION_MODEL_PATH):
            _prediction_model = joblib.load(PREDICTION_MODEL_PATH)
            print(f"✅ Loaded prediction model from {PREDICTION_MODEL_PATH}")
        else:
            # Use placeholder model if joblib not available or file doesn't exist
            _prediction_model = PlaceholderPredictionModel()
            print("⚠️  Using rule-based prediction (prediction_model.pkl not found)")
    return _prediction_model




class PlaceholderQuestionModel:
    """
    Placeholder model for question generation when actual model is not available.
    Uses rule-based logic to determine next question domain and difficulty.
    """
    
    def predict(self, features: np.ndarray) -> np.ndarray:
        """
        Generate next question parameters based on features.
        
        Args:
        Args:
            features: Array of shape (1, 7) with:
                [last_correct, last_response_time, last_diff_easy, last_diff_medium, 
                 last_diff_hard, session_accuracy, current_domain]
        
        Returns:
            Array of shape (2,) with [domain_index, difficulty_index]
            domain_index: 0=reading, 1=writing, 2=math, 3=attention
            difficulty_index: 0=easy, 1=medium, 2=hard
        """
        last_correct = features[0][0]
        last_response_time = features[0][1]
        last_diff_easy = features[0][2]
        last_diff_medium = features[0][3]
        last_diff_hard = features[0][4]
        # session_accuracy = features[0][5]  # Unused in simple logic
        current_domain = features[0][6]
        
        # Determine current difficulty from one-hot encoding
        if last_diff_easy:
            current_difficulty = 0  # easy
        elif last_diff_medium:
            current_difficulty = 1  # medium
        else:
            current_difficulty = 2  # hard
        
        # Adaptive difficulty logic (matching DB/logic.py thresholds)
        if last_correct and last_response_time < 900:
            # Fast and correct → harder
            next_difficulty = min(2, current_difficulty + 1)
        elif not last_correct or last_response_time > 1400:
            # Wrong or slow → easier
            next_difficulty = max(0, current_difficulty - 1)
        else:
            # Keep same difficulty
            next_difficulty = current_difficulty
        
        # Domain rotation: simple cycle since we don't have counts in features anymore
        next_domain = (int(current_domain) + 1) % 4
        
        return np.array([next_domain, next_difficulty])


class PlaceholderPredictionModel:
    """
    Placeholder model for final prediction when actual model is not available.
    Returns risk scores based on feature analysis.
    """
    
    def predict(self, features: np.ndarray) -> np.ndarray:
        """
        Generate prediction based on features.
        Returns array of [dyslexia_risk, dyscalculia_risk, attention_risk]
        """
        # Extract feature values
        accuracy = features[0][0] if features.shape[1] > 0 else 0.5
        avg_response_time = features[0][1] if features.shape[1] > 1 else 2000
        error_rate = features[0][2] if features.shape[1] > 2 else 0.5
        reading_accuracy = features[0][4] if features.shape[1] > 4 else 0.5
        math_accuracy = features[0][5] if features.shape[1] > 5 else 0.5
        letter_reversal_count = features[0][6] if features.shape[1] > 6 else 0
        
        # Simple rule-based risk calculation
        dyslexia_risk = min(1.0, 
            (1 - accuracy) * 0.4 + 
            (1 - reading_accuracy) * 0.3 + 
            (letter_reversal_count / 5) * 0.3
        )
        
        dyscalculia_risk = min(1.0, 
            (1 - accuracy) * 0.3 + 
            (1 - math_accuracy) * 0.4 + 
            (avg_response_time / 5000) * 0.3
        )
        
        attention_risk = min(1.0, 
            (avg_response_time / 5000) * 0.5 + 
            (1 - accuracy) * 0.3 +
            (error_rate * 0.2)
        )
        
        return np.array([[dyslexia_risk, dyscalculia_risk, attention_risk]])


def extract_question_features(
    session_id: str,
    last_question_id: str = None,
    correct: bool = None,
    response_time_ms: int = None
) -> np.ndarray:
    """
    Extract features for question generation model.
    
    Args:
        session_id: Current session ID
        last_question_id: ID of last question answered
        correct: Whether last answer was correct
        response_time_ms: Response time in milliseconds
    
    Returns:
        numpy array of shape (1, 10) with features for question model
    """
    from .models import UserResponse, Question
    
    # Get all responses for this session
    responses = UserResponse.objects.filter(session_id=session_id).order_by('answered_at')
    
    # Default values for first question
    if not last_question_id or correct is None or response_time_ms is None:
        return np.array([[
            1,      # last_correct (assume correct for first question)
            1000,   # last_response_time
            1, 0, 0,  # last_difficulty (easy)
            1.0,    # session_accuracy (100% for first)
            0       # current_domain (reading)
        ]])
    
    # Get last question difficulty
    try:
        last_question = Question.objects.get(question_id=last_question_id)
        last_difficulty = last_question.difficulty
    except Question.DoesNotExist:
        last_difficulty = 'medium'
    
    # One-hot encode difficulty
    diff_easy = 1 if last_difficulty == 'easy' else 0
    diff_medium = 1 if last_difficulty == 'medium' else 0
    diff_hard = 1 if last_difficulty == 'hard' else 0
    
    # Calculate session accuracy
    if responses.exists():
        total = responses.count()
        correct_count = responses.filter(correct=True).count()
        session_accuracy = correct_count / total if total > 0 else 0.5
    else:
        session_accuracy = 1.0 if correct else 0.0
    
    # Map domain to integer (only 3 domains for assessment)
    domain_map = {'reading': 0, 'math': 1, 'attention': 2}
    
    # Get last domain
    last_domain = 'reading' # Default
    if last_question_id:
        try:
             # We already fetched last_question above if it existed, but let's be safe
             q_obj = Question.objects.get(question_id=last_question_id)
             last_domain = q_obj.domain
        except Question.DoesNotExist:
             pass
             
    cur_domain_val = domain_map.get(last_domain, 0)

    # 7 features: [last_correct, last_response_time, diff_easy, diff_medium, diff_hard, session_accuracy, current_domain]
    features = np.array([[
        1 if correct else 0,  # last_correct
        response_time_ms,     # last_response_time
        diff_easy,            # last_difficulty_easy
        diff_medium,          # last_difficulty_medium
        diff_hard,            # last_difficulty_hard
        session_accuracy,     # session_accuracy
        cur_domain_val        # current_domain
    ]])
    
    return features


def extract_features(responses: List[Dict[str, Any]]) -> np.ndarray:
    """
    Extract ML features from user responses.
    
    Features extracted:
    1. accuracy - Overall accuracy rate
    2. avg_response_time - Average response time in ms
    3. error_rate - Rate of incorrect answers
    4. consistency - Standard deviation of response times
    5. reading_accuracy - Accuracy on reading questions
    6. math_accuracy - Accuracy on math questions
    7. letter_reversal_count - Count of letter reversal mistakes
    8. confidence_mismatch - Low confidence + correct OR high confidence + incorrect
    
    Args:
        responses: List of response dictionaries
        
    Returns:
        numpy array of features
    """
    if not responses:
        # Return default features
        return np.array([[0.5, 2000, 0.5, 500, 0.5, 0.5, 0, 0]])
    
    # Calculate accuracy
    total = len(responses)
    correct_count = sum(1 for r in responses if r.get('correct', False))
    accuracy = correct_count / total if total > 0 else 0.5
    
    # Calculate average response time
    response_times = [r.get('response_time_ms', 2000) for r in responses]
    avg_response_time = np.mean(response_times) if response_times else 2000
    
    # Error rate
    error_rate = 1 - accuracy
    
    # Consistency (std dev of response times)
    consistency = np.std(response_times) if len(response_times) > 1 else 500
    
    # Domain-specific accuracy
    reading_responses = [r for r in responses if r.get('domain') == 'reading']
    reading_correct = sum(1 for r in reading_responses if r.get('correct', False))
    reading_accuracy = reading_correct / len(reading_responses) if reading_responses else 0.5
    
    math_responses = [r for r in responses if r.get('domain') == 'math']
    math_correct = sum(1 for r in math_responses if r.get('correct', False))
    math_accuracy = math_correct / len(math_responses) if math_responses else 0.5
    
    # Letter reversal count (from mistake patterns)
    letter_reversal_count = sum(
        1 for r in responses 
        if r.get('mistake_type') == 'letter_reversal'
    )
    
    # Confidence mismatch
    confidence_mismatch = sum(
        1 for r in responses
        if (r.get('confidence') == 'low' and r.get('correct')) or
           (r.get('confidence') == 'high' and not r.get('correct'))
    )
    
    features = np.array([[
        accuracy,
        avg_response_time,
        error_rate,
        consistency,
        reading_accuracy,
        math_accuracy,
        letter_reversal_count,
        confidence_mismatch
    ]])
    
    return features


def get_next_question_ml(
    session_id: str,
    last_question_id: str = None,
    correct: bool = None,
    response_time_ms: int = None
) -> tuple:
    """
    Get next question domain and difficulty using ML model.
    
    Args:
        session_id: Current session ID
        last_question_id: ID of last question answered
        correct: Whether last answer was correct
        response_time_ms: Response time in milliseconds
    
    Returns:
        Tuple of (domain, difficulty) as strings
    """
    model = load_question_model()
    features = extract_question_features(session_id, last_question_id, correct, response_time_ms)
    
    # Get prediction
    prediction = model.predict(features)
    
    # Handle different output shapes
    if len(prediction.shape) == 2:
        domain_idx = int(prediction[0][0])
        difficulty_idx = int(prediction[0][1])
    else:
        domain_idx = int(prediction[0])
        difficulty_idx = int(prediction[1])
    
    # Map indices to strings
    domains = ['reading', 'writing', 'math', 'attention']
    difficulties = ['easy', 'medium', 'hard']
    
    domain = domains[domain_idx] if 0 <= domain_idx < 4 else 'reading'
    difficulty = difficulties[difficulty_idx] if 0 <= difficulty_idx < 3 else 'medium'
    
    return (domain, difficulty)


def get_prediction(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Get risk prediction from ML model (using team's risk_classifier.pkl).
    
    Args:
        responses: List of user response dictionaries
        
    Returns:
        Dictionary with risk, confidence_level, and key_insights
    """
    model = load_prediction_model()
    
    if not responses:
        return {
            'risk': 'low-risk',
            'confidence_level': 'low',
            'key_insights': ['Insufficient data for assessment'],
            'scores': {'dyslexia': 0, 'dyscalculia': 0, 'attention': 0}
        }
    
    # Calculate features for risk_classifier model
    # Expected features: reading_acc, math_acc, focus_acc, avg_time_ms, rev_rate, pv_rate, impulse_rate
    
    total = len(responses)
    
    # Domain-specific accuracy
    reading_responses = [r for r in responses if r.get('domain') in ['reading', 'writing']]
    math_responses = [r for r in responses if r.get('domain') == 'math']
    focus_responses = [r for r in responses if r.get('domain') in ['attention', 'focus']]
    
    reading_acc = sum(1 for r in reading_responses if r.get('correct')) / len(reading_responses) if reading_responses else 0.5
    math_acc = sum(1 for r in math_responses if r.get('correct')) / len(math_responses) if math_responses else 0.5
    focus_acc = sum(1 for r in focus_responses if r.get('correct')) / len(focus_responses) if focus_responses else 0.5
    
    # Average time
    avg_time_ms = sum(r.get('response_time_ms', 2000) for r in responses) / total
    
    # Reversal rate (letter_reversal mistakes)
    reversal_count = sum(1 for r in responses if r.get('mistake_type') == 'letter_reversal')
    rev_rate = reversal_count / total
    
    # Position/visual rate (other visual mistakes)
    pv_count = sum(1 for r in responses if r.get('mistake_type') in ['number_reversal', 'substitution'])
    pv_rate = pv_count / total
    
    # Impulse rate (fast incorrect answers)
    impulse_count = sum(1 for r in responses if not r.get('correct') and r.get('response_time_ms', 2000) < 1000)
    impulse_rate = impulse_count / total
    
    # Create DataFrame with exact column names
    features = pd.DataFrame([{
        "reading_acc": reading_acc,
        "math_acc": math_acc,
        "focus_acc": focus_acc,
        "avg_time_ms": avg_time_ms,
        "rev_rate": rev_rate,
        "pv_rate": pv_rate,
        "impulse_rate": impulse_rate
    }])
    
    # Get prediction
    prediction = model.predict(features)[0]  # Returns label like "Dyslexia Risk"
    
    # Get confidence
    if hasattr(model, 'predict_proba'):
        probs = model.predict_proba(features)[0]
        confidence_score = max(probs) * 100
        
        if confidence_score > 80:
            confidence_level = 'high'
        elif confidence_score > 60:
            confidence_level = 'moderate'
        else:
            confidence_level = 'low'
    else:
        confidence_level = 'moderate'
        confidence_score = 70
    
    # Map prediction to our format
    label_map = {
        'Low Risk': 'low-risk',
        'Dyslexia Risk': 'dyslexia-risk',
        'Dyscalculia Risk': 'dyscalculia-risk',
        'Attention Risk': 'attention-risk'
    }
    
    final_label = label_map.get(prediction, 'low-risk')
    
    # Generate insights
    key_insights = []
    
    if rev_rate > 0.2:
        key_insights.append(f"Frequent letter reversals observed ({int(rev_rate*100)}% of responses)")
    
    if avg_time_ms > 5000:
        key_insights.append("Response time significantly slower than average")
    elif avg_time_ms < 1000 and impulse_rate > 0.3:
        key_insights.append("High impulsivity detected - fast but inaccurate responses")
    
    if reading_acc < 0.5:
        key_insights.append(f"Reading accuracy below expected level ({reading_acc*100:.0f}%)")
    
    if math_acc < 0.5:
        key_insights.append(f"Math accuracy below expected level ({math_acc*100:.0f}%)")
    
    if focus_acc < 0.5:
        key_insights.append(f"Attention/focus accuracy below expected level ({focus_acc*100:.0f}%)")
    
    if not key_insights:
        if final_label == 'low-risk':
            key_insights.append("Performance within normal range across all domains")
        else:
            key_insights.append("Some areas may benefit from additional assessment")
    
    # Create risk scores (approximate from the prediction)
    scores = {
        'dyslexia': 0.7 if 'dyslexia' in final_label.lower() else 0.2,
        'dyscalculia': 0.7 if 'dyscalculia' in final_label.lower() else 0.2,
        'attention': 0.7 if 'attention' in final_label.lower() else 0.2
    }
    
    return {
        'risk': final_label,
        'confidence_level': confidence_level,
        'key_insights': key_insights[:5],
        'scores': scores
    }



def generate_insights(
    responses: List[Dict[str, Any]], 
    features: np.ndarray,
    risks: Dict[str, float]
) -> List[str]:
    """Generate key insights based on analysis."""
    insights = []
    
    accuracy = features[0][0]
    avg_response_time = features[0][1]
    letter_reversal_count = int(features[0][6])
    
    # Letter reversal insight
    if letter_reversal_count >= 2:
        insights.append(f"Frequent letter reversals observed ({letter_reversal_count} instances)")
    
    # Reading speed insight
    if avg_response_time > 3000:
        insights.append("Reading speed slower than age norm")
    
    # Accuracy insight
    if accuracy < 0.6:
        insights.append(f"Overall accuracy below expected level ({accuracy*100:.0f}%)")
    
    # Domain-specific insights
    reading_accuracy = features[0][4]
    math_accuracy = features[0][5]
    
    if reading_accuracy < 0.5 and reading_accuracy < math_accuracy:
        insights.append("Difficulty with reading-based tasks compared to math")
    
    if math_accuracy < 0.5 and math_accuracy < reading_accuracy:
        insights.append("Difficulty with math-based tasks compared to reading")
    
    # Consistency insight
    consistency = features[0][3]
    if consistency > 1500:
        insights.append("High variability in response times may indicate attention difficulties")
    
    # Add default insight if none generated
    if not insights:
        if accuracy > 0.7:
            insights.append("Performance within normal range")
        else:
            insights.append("Some areas may benefit from additional assessment")
    
    return insights[:5]  # Limit to 5 insights
