import joblib
import pandas as pd
import numpy as np

# Load the trained model
model = joblib.load("risk_classifier.pkl")

def predict_student_risk(reading_acc, math_acc, focus_acc, avg_time, rev_rate, pv_rate, impulse_rate):
    """
    Takes student performance metrics and returns a risk prediction.
    """
    # Create a DataFrame with the exact same column names as training
    features = pd.DataFrame([{
        "reading_acc": reading_acc,
        "math_acc": math_acc,
        "focus_acc": focus_acc,
        "avg_time_ms": avg_time,
        "rev_rate": rev_rate,
        "pv_rate": pv_rate,
        "impulse_rate": impulse_rate
    }])
    
    # Predict
    prediction = model.predict(features)[0]
    
    # Get Probability (Confidence score)
    probs = model.predict_proba(features)[0]
    confidence = max(probs) * 100
    
    return prediction, confidence

# --- TEST SCENARIO ---
if __name__ == "__main__":
    print("🏥 Running AI Diagnosis Simulation...\n")

    # CASE 1: The "Dyslexia" Profile
    # Low Reading Acc, Slow Time, High Reversals (0.6)
    pred, conf = predict_student_risk(
        reading_acc=0.45, math_acc=0.90, focus_acc=0.85, 
        avg_time=6000, 
        rev_rate=0.6, pv_rate=0.05, impulse_rate=0.1
    )
    print(f"Test Case 1 (Reversals): {pred} ({conf:.1f}% Confidence)")

    # CASE 2: The "ADHD" Profile
    # Fast Time (800ms), High Impulsivity (0.8)
    pred, conf = predict_student_risk(
        reading_acc=0.6, math_acc=0.6, focus_acc=0.4, 
        avg_time=800, 
        rev_rate=0.1, pv_rate=0.1, impulse_rate=0.8
    )
    print(f"Test Case 2 (Impulsive): {pred} ({conf:.1f}% Confidence)")