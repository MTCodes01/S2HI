import pandas as pd
import numpy as np
import random
import os

# --- CONFIGURATION ---
SAMPLES_PER_CLASS = 2000 # Total 8000 samples

def generate_clinical_dataset():
    data = []
    
    # -----------------------------------------
    # CLASS 0: LOW RISK (Healthy Performance)
    # -----------------------------------------
    print("generating Low Risk profiles...")
    for _ in range(SAMPLES_PER_CLASS):
        row = {
            "reading_acc": random.uniform(0.8, 1.0),   # High Accuracy
            "math_acc": random.uniform(0.8, 1.0),
            "focus_acc": random.uniform(0.8, 1.0),
            "avg_time_ms": random.uniform(2000, 5000), # Normal Speed
            "rev_rate": random.uniform(0.0, 0.1),      # Low Reversals
            "pv_rate": random.uniform(0.0, 0.1),       # Low Place Value Errors
            "impulse_rate": random.uniform(0.0, 0.1),  # Low Impulsivity
            "label": "Low Risk"
        }
        data.append(row)

    # -----------------------------------------
    # CLASS 1: DYSLEXIA RISK (Reading Struggle)
    # -----------------------------------------
    print("generating Dyslexia Risk profiles...")
    for _ in range(SAMPLES_PER_CLASS):
        row = {
            "reading_acc": random.uniform(0.2, 0.6),   # Low Reading Acc
            "math_acc": random.uniform(0.7, 1.0),      # Math often normal
            "focus_acc": random.uniform(0.6, 1.0),
            "avg_time_ms": random.uniform(4000, 9000), # Slow reading
            "rev_rate": random.uniform(0.4, 0.9),      # HIGH Reversal Rate (The Key Signal)
            "pv_rate": random.uniform(0.0, 0.2),
            "impulse_rate": random.uniform(0.0, 0.2),
            "label": "Dyslexia Risk"
        }
        data.append(row)

    # -----------------------------------------
    # CLASS 2: DYSCALCULIA RISK (Math Struggle)
    # -----------------------------------------
    print("generating Dyscalculia Risk profiles...")
    for _ in range(SAMPLES_PER_CLASS):
        row = {
            "reading_acc": random.uniform(0.7, 1.0),   # Reading often normal
            "math_acc": random.uniform(0.2, 0.55),     # Low Math Acc
            "focus_acc": random.uniform(0.6, 1.0),
            "avg_time_ms": random.uniform(4000, 10000),# Slow math
            "rev_rate": random.uniform(0.0, 0.2),
            "pv_rate": random.uniform(0.4, 0.9),       # HIGH Place Value Errors (The Key Signal)
            "impulse_rate": random.uniform(0.0, 0.2),
            "label": "Dyscalculia Risk"
        }
        data.append(row)

    # -----------------------------------------
    # CLASS 3: ATTENTION RISK (ADHD Traits)
    # -----------------------------------------
    print("generating Attention Risk profiles...")
    for _ in range(SAMPLES_PER_CLASS):
        row = {
            "reading_acc": random.uniform(0.5, 0.8),   # Inconsistent
            "math_acc": random.uniform(0.5, 0.8),      # Inconsistent
            "focus_acc": random.uniform(0.3, 0.6),     # Low Focus Acc
            "avg_time_ms": random.uniform(500, 1500),  # VERY FAST (Impulsive)
            "rev_rate": random.uniform(0.1, 0.3),
            "pv_rate": random.uniform(0.1, 0.3),
            "impulse_rate": random.uniform(0.5, 0.95), # HIGH Impulsivity (The Key Signal)
            "label": "Attention Risk"
        }
        data.append(row)

    # Convert to DataFrame and Shuffle
    df = pd.DataFrame(data)
    df = df.sample(frac=1).reset_index(drop=True) # Shuffle

    # Save
    csv_path = "clinical_data.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ Generated {len(df)} clinical profiles. Saved to {os.getcwd()}/{csv_path}")

if __name__ == "__main__":
    generate_clinical_dataset()