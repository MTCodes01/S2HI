"""
ML model integration utilities.
Handles model loading, feature extraction, and prediction.
"""
import os
import numpy as np
from typing import Dict, List, Any
from django.conf import settings

# Try to import joblib, fall back to placeholder if not available
try:
    import joblib
    HAS_JOBLIB = True
except ImportError:
    HAS_JOBLIB = False

# Path to the ML model
MODEL_PATH = os.path.join(settings.BASE_DIR, 'ld_model.pkl')

# Global model instance
_model = None


def load_model():
    """Load the ML model from disk."""
    global _model
    if _model is None:
        if HAS_JOBLIB and os.path.exists(MODEL_PATH):
            _model = joblib.load(MODEL_PATH)
        else:
            # Use placeholder model if joblib not available or file doesn't exist
            _model = PlaceholderModel()
    return _model


class PlaceholderModel:
    """
    Placeholder model for development/testing when actual model is not available.
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
        
        # Simple rule-based risk calculation
        dyslexia_risk = min(1.0, (1 - accuracy) * 0.7 + (error_rate * 0.3))
        dyscalculia_risk = min(1.0, (1 - accuracy) * 0.5 + (avg_response_time / 5000) * 0.5)
        attention_risk = min(1.0, (avg_response_time / 5000) * 0.6 + (1 - accuracy) * 0.4)
        
        return np.array([[dyslexia_risk, dyscalculia_risk, attention_risk]])


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


def get_prediction(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Get risk prediction from ML model.
    
    Args:
        responses: List of user response dictionaries
        
    Returns:
        Dictionary with risk, confidence_level, and key_insights
    """
    model = load_model()
    features = extract_features(responses)
    
    # Get prediction
    prediction = model.predict(features)
    
    dyslexia_risk = float(prediction[0][0])
    dyscalculia_risk = float(prediction[0][1])
    attention_risk = float(prediction[0][2])
    
    # Determine primary risk
    risks = {
        'dyslexia-risk': dyslexia_risk,
        'dyscalculia-risk': dyscalculia_risk,
        'attention-risk': attention_risk
    }
    
    max_risk_label = max(risks, key=risks.get)
    max_risk_score = risks[max_risk_label]
    
    # Determine confidence level
    if max_risk_score > 0.7:
        confidence_level = 'high'
    elif max_risk_score > 0.4:
        confidence_level = 'moderate'
    else:
        confidence_level = 'low'
    
    # Generate insights
    key_insights = generate_insights(responses, features, risks)
    
    # Determine final label
    if max_risk_score < 0.3:
        final_label = 'low-risk'
    else:
        final_label = max_risk_label
    
    return {
        'risk': final_label,
        'confidence_level': confidence_level,
        'key_insights': key_insights,
        'scores': {
            'dyslexia': dyslexia_risk,
            'dyscalculia': dyscalculia_risk,
            'attention': attention_risk
        }
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
