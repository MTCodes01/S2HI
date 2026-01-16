"""
Script to create placeholder ML model for testing.
Run this once to generate ld_model.pkl
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier


def create_placeholder_model():
    """
    Create a simple placeholder ML model for testing.
    This generates a random forest model that returns risk scores.
    """
    # Create synthetic training data
    np.random.seed(42)
    n_samples = 100
    
    # Features: accuracy, avg_response_time, error_rate, consistency,
    #           reading_accuracy, math_accuracy, letter_reversal_count, confidence_mismatch
    X = np.random.rand(n_samples, 8)
    
    # Scale features to realistic ranges
    X[:, 1] *= 5000  # avg_response_time (0-5000ms)
    X[:, 3] *= 2000  # consistency
    X[:, 6] *= 5     # letter_reversal_count
    X[:, 7] *= 3     # confidence_mismatch
    
    # Generate synthetic labels based on features
    # This will be replaced by actual trained model
    y = np.zeros((n_samples, 3))  # [dyslexia, dyscalculia, attention]
    
    for i in range(n_samples):
        # Dyslexia risk: based on accuracy and letter reversals
        y[i, 0] = min(1.0, (1 - X[i, 0]) * 0.6 + X[i, 6] / 5 * 0.4)
        
        # Dyscalculia risk: based on math accuracy and response time
        y[i, 1] = min(1.0, (1 - X[i, 5]) * 0.5 + X[i, 1] / 5000 * 0.5)
        
        # Attention risk: based on consistency and response time
        y[i, 2] = min(1.0, X[i, 3] / 2000 * 0.5 + X[i, 1] / 5000 * 0.5)
    
    # Create a simple model wrapper class
    class PlaceholderLDModel:
        def __init__(self):
            self.name = "LD Screening Placeholder Model"
            self.version = "1.0.0"
        
        def predict(self, X):
            """
            Predict risk scores based on features.
            Returns array of shape (n_samples, 3) with:
            [dyslexia_risk, dyscalculia_risk, attention_risk]
            """
            results = []
            for features in X:
                accuracy = features[0]
                avg_response_time = features[1]
                error_rate = features[2]
                consistency = features[3]
                reading_accuracy = features[4]
                math_accuracy = features[5]
                letter_reversal_count = features[6]
                confidence_mismatch = features[7]
                
                # Dyslexia risk
                dyslexia = min(1.0, max(0.0,
                    (1 - accuracy) * 0.4 +
                    (1 - reading_accuracy) * 0.3 +
                    letter_reversal_count / 5 * 0.3
                ))
                
                # Dyscalculia risk
                dyscalculia = min(1.0, max(0.0,
                    (1 - accuracy) * 0.3 +
                    (1 - math_accuracy) * 0.4 +
                    avg_response_time / 5000 * 0.3
                ))
                
                # Attention risk
                attention = min(1.0, max(0.0,
                    consistency / 2000 * 0.4 +
                    avg_response_time / 5000 * 0.3 +
                    confidence_mismatch / 3 * 0.3
                ))
                
                results.append([dyslexia, dyscalculia, attention])
            
            return np.array(results)
    
    # Create and save model
    model = PlaceholderLDModel()
    model_path = os.path.join(os.path.dirname(__file__), 'ld_model.pkl')
    joblib.dump(model, model_path)
    print(f"Model saved to: {model_path}")
    
    return model


if __name__ == '__main__':
    model = create_placeholder_model()
    
    # Test the model
    test_features = np.array([[
        0.6,    # accuracy
        2500,   # avg_response_time
        0.4,    # error_rate
        800,    # consistency
        0.55,   # reading_accuracy
        0.65,   # math_accuracy
        2,      # letter_reversal_count
        1       # confidence_mismatch
    ]])
    
    prediction = model.predict(test_features)
    print(f"\nTest prediction:")
    print(f"  Dyslexia risk: {prediction[0][0]:.2f}")
    print(f"  Dyscalculia risk: {prediction[0][1]:.2f}")
    print(f"  Attention risk: {prediction[0][2]:.2f}")
