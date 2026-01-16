import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

def train_risk_model():
    # 1. Load the Clinical Data
    csv_path = "clinical_data.csv"
    if not os.path.exists(csv_path):
        print("❌ Error: 'clinical_data.csv' not found. Run generate_clinical_data.py first!")
        return

    print(f"📊 Loading clinical profiles from {csv_path}...")
    df = pd.read_csv(csv_path)

    # 2. Separate Symptoms (X) and Diagnosis (y)
    # X = The symptoms (Accuracy, Speed, Mistake Rates)
    X = df[[
        "reading_acc", "math_acc", "focus_acc", 
        "avg_time_ms", 
        "rev_rate", "pv_rate", "impulse_rate"
    ]]
    
    # y = The Diagnosis (Low Risk, Dyslexia, etc.)
    y = df["label"]

    # 3. Initialize the Brain (Random Forest)
    # n_estimators=100 means we use 100 "decision trees" to vote on the diagnosis
    rf = RandomForestClassifier(n_estimators=100, random_state=42)

    # 4. Train the Model
    print("🧠 Training the Risk Classifier...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    rf.fit(X_train, y_train)

    # 5. Evaluate Performance
    print("\n🎯 Model Evaluation:")
    accuracy = rf.score(X_test, y_test)
    print(f"   Accuracy: {accuracy:.2%}")
    
    # Show detailed report (Precision/Recall for each condition)
    y_pred = rf.predict(X_test)
    print("\n📝 detailed Report:")
    print(classification_report(y_test, y_pred))

    # 6. Save the Brain
    joblib.dump(rf, "risk_classifier.pkl")
    print(f"✅ Success! Model saved as 'risk_classifier.pkl' in {os.getcwd()}")

if __name__ == "__main__":
    train_risk_model()