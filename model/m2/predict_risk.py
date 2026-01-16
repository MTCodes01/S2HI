import joblib
import pandas as pd
import numpy as np
import os

# Load the trained model
# Using os.path to make sure it finds the file if run from different folders
model_path = "risk_classifier.pkl"
if not os.path.exists(model_path):
    # Fallback if running from main folder
    model_path = "model/model2/risk_classifier.pkl"

model = joblib.load(model_path)

def predict_student_risk(reading_acc, math_acc, focus_acc, avg_time, rev_rate, pv_rate, impulse_rate):
    """
    Takes student performance metrics and returns a risk prediction.
    """
    
    # --- 🛡️ SAFETY CHECK: Normalize Inputs ---
    # If the backend sends percentage as 0-100 (e.g. 85.0), convert to 0.0-1.0
    if reading_acc > 1.0: reading_acc /= 100.0
    if math_acc > 1.0:    math_acc /= 100.0
    if focus_acc > 1.0:   focus_acc /= 100.0
    
    # Same check for rates if they might come in as percentages
    if rev_rate > 1.0:     rev_rate /= 100.0
    if pv_rate > 1.0:      pv_rate /= 100.0
    if impulse_rate > 1.0: impulse_rate /= 100.0
    # ------------------------------------------

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
    pred, conf = predict_student_risk(
        reading_acc=0.45, math_acc=0.90, focus_acc=0.85, 
        avg_time=6000, 
        rev_rate=0.6, pv_rate=0.05, impulse_rate=0.1
    )
    print(f"Test Case 1 (Reversals): {pred} ({conf:.1f}% Confidence)")

    # CASE 2: The "ADHD" Profile
    pred, conf = predict_student_risk(
        reading_acc=0.6, math_acc=0.6, focus_acc=0.4, 
        avg_time=800, 
        rev_rate=0.1, pv_rate=0.1, impulse_rate=0.8
    )
    print(f"Test Case 2 (Impulsive): {pred} ({conf:.1f}% Confidence)")
    
    # CASE 3: The "Integer Input" Test (The Safety Check Test)
    # We send '90' instead of '0.90' to see if the code fixes it
    pred, conf = predict_student_risk(
        reading_acc=90, math_acc=90, focus_acc=90,  # <-- INTEGERS
        avg_time=4000, 
        rev_rate=0, pv_rate=0, impulse_rate=0
    )
    print(f"Test Case 3 (Safety Check): {pred} (Should be Low Risk)")