import pandas as pd
import random
import os

SAMPLES_PER_CLASS = 3000 

def generate_clinical_dataset():
    data = []
    print("🏥 Generating SHARP clinical profiles...")
    
    # 1. LOW RISK (Healthy) -> High Acc, Normal Speed, Zero Mistakes
    for _ in range(SAMPLES_PER_CLASS):
        row = {
            "reading_acc": random.uniform(0.90, 1.0), # Very High
            "math_acc":    random.uniform(0.90, 1.0),
            "focus_acc":   random.uniform(0.90, 1.0),
            "avg_time_ms": random.uniform(3000, 6000), 
            "rev_rate":    0.0,  # FORCE ZERO
            "pv_rate":     0.0,  # FORCE ZERO
            "impulse_rate":0.0,  # FORCE ZERO
            "label": "Low Risk"
        }
        data.append(row)

    # 2. DYSLEXIA (Reading Only) -> Low Read Acc + HIGH Reversals
    for _ in range(SAMPLES_PER_CLASS):
        row = {
            "reading_acc": random.uniform(0.30, 0.60), # Distinctly Low
            "math_acc":    random.uniform(0.80, 1.0),  # High
            "focus_acc":   random.uniform(0.80, 1.0),
            "avg_time_ms": random.uniform(6000, 12000),# Slow
            "rev_rate":    random.uniform(0.40, 0.90), # VERY HIGH
            "pv_rate":     random.uniform(0.0, 0.05),
            "impulse_rate":random.uniform(0.0, 0.10),
            "label": "Dyslexia Risk"
        }
        data.append(row)

    # 3. DYSCALCULIA (Math Only) -> Low Math Acc + HIGH Place Value
    for _ in range(SAMPLES_PER_CLASS):
        row = {
            "reading_acc": random.uniform(0.80, 1.0),
            "math_acc":    random.uniform(0.30, 0.55), # Distinctly Low
            "focus_acc":   random.uniform(0.80, 1.0),
            "avg_time_ms": random.uniform(6000, 15000),# Slow
            "rev_rate":    random.uniform(0.0, 0.05),
            "pv_rate":     random.uniform(0.50, 0.95), # VERY HIGH
            "impulse_rate":random.uniform(0.0, 0.10),
            "label": "Dyscalculia Risk"
        }
        data.append(row)

    # 4. ATTENTION (Focus Only) -> Low Focus + Fast Speed + HIGH Impulse
    for _ in range(SAMPLES_PER_CLASS):
        row = {
            "reading_acc": random.uniform(0.60, 0.90), # Okayish
            "math_acc":    random.uniform(0.60, 0.90), # Okayish
            "focus_acc":   random.uniform(0.20, 0.50), # LOW
            "avg_time_ms": random.uniform(500, 1500),  # SUPER FAST
            "rev_rate":    random.uniform(0.0, 0.15),
            "pv_rate":     random.uniform(0.0, 0.15),
            "impulse_rate":random.uniform(0.60, 1.0),  # VERY HIGH
            "label": "Attention Risk"
        }
        data.append(row)

    # Shuffle & Save
    df = pd.DataFrame(data).sample(frac=1).reset_index(drop=True)
    df.to_csv("clinical_data.csv", index=False)
    print("✅ Generated non-overlapping data.")

if __name__ == "__main__":
    generate_clinical_dataset()