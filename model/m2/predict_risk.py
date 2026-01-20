import joblib
import pandas as pd
import numpy as np
import os

# 1. Load the Trained Model
# We check multiple paths to ensure it works from different folders
model_path = "risk_classifier.pkl"
if not os.path.exists(model_path):
    model_path = "model/model2/risk_classifier.pkl"

if not os.path.exists(model_path):
    print("❌ CRITICAL ERROR: Could not find 'risk_classifier.pkl'.")
    print("   👉 Run 'train_model_m2.py' first!")
    exit()

model = joblib.load(model_path)

def predict_student_risk(reading_acc, math_acc, focus_acc, avg_time, rev_rate, pv_rate, impulse_rate):
    """
    Takes student performance metrics and returns a risk prediction.
    Args:
        reading_acc (float): 0.0 to 1.0
        math_acc (float):    0.0 to 1.0
        focus_acc (float):   0.0 to 1.0
        avg_time (int):      Average response time in ms
        rev_rate (float):    Reversal Error Rate (e.g. b/d swaps)
        pv_rate (float):     Place Value Error Rate (Math specific)
        impulse_rate (float): Impulsivity Rate (Focus specific)
    """
    
    # --- 🛡️ SAFETY CHECK: Normalize Inputs ---
    # Convert percentages (e.g., 85.0) to decimals (0.85) automatically
    if reading_acc > 1.0: reading_acc /= 100.0
    if math_acc > 1.0:    math_acc /= 100.0
    if focus_acc > 1.0:   focus_acc /= 100.0
    
    if rev_rate > 1.0:     rev_rate /= 100.0
    if pv_rate > 1.0:      pv_rate /= 100.0
    if impulse_rate > 1.0: impulse_rate /= 100.0
    # ------------------------------------------

    # Create DataFrame with exact columns expected by the model
    features = pd.DataFrame([{
        "reading_acc": reading_acc,
        "math_acc": math_acc,
        "focus_acc": focus_acc,
        "avg_time_ms": avg_time,
        "rev_rate": rev_rate,
        "pv_rate": pv_rate,
        "impulse_rate": impulse_rate
    }])
    
    # Predict Label
    prediction = model.predict(features)[0]
    
    # Get Confidence Score (Probability)
    probs = model.predict_proba(features)[0]
    confidence = max(probs) * 100
    
    return prediction, confidence

# --- TEST SCENARIOS ---
if __name__ == "__main__":
    print("🏥 Running AI Diagnosis Simulation...\n")

    # CASE 1: Dyslexia Risk
    # Low Reading + High Reversals (b/d confusion)
    pred, conf = predict_student_risk(
        reading_acc=0.45, math_acc=0.90, focus_acc=0.85, 
        avg_time=6000, 
        rev_rate=0.6, pv_rate=0.05, impulse_rate=0.1
    )
    print(f"Test Case 1 (Reading Issue): {pred} ({conf:.1f}% Confidence)")

    # CASE 2: Dyscalculia Risk (NEW)
    # Good Reading + LOW Math + High Place Value Errors
    pred, conf = predict_student_risk(
        reading_acc=0.90, math_acc=0.40, focus_acc=0.85, 
        avg_time=8000, 
        rev_rate=0.05, pv_rate=0.80, impulse_rate=0.1
    )
    print(f"Test Case 2 (Math Issue):    {pred} ({conf:.1f}% Confidence)")

    # CASE 3: Attention/ADHD Risk
    # Fast Speed + Low Focus + High Impulsivity
    pred, conf = predict_student_risk(
        reading_acc=0.6, math_acc=0.6, focus_acc=0.4, 
        avg_time=800, 
        rev_rate=0.1, pv_rate=0.1, impulse_rate=0.8
    )
    print(f"Test Case 3 (Focus Issue):   {pred} ({conf:.1f}% Confidence)")
    
    # CASE 4: Low Risk (Healthy)
    # High Accuracy across board
    pred, conf = predict_student_risk(
        reading_acc=0.95, math_acc=0.95, focus_acc=0.95, 
        avg_time=4000, 
        rev_rate=0.0, pv_rate=0.0, impulse_rate=0.0
    )
    print(f"Test Case 4 (Healthy):       {pred} ({conf:.1f}% Confidence)")