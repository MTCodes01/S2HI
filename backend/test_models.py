"""
Test script for ML models.
Run this to verify that your models work correctly with the backend.
"""
import os
import sys
import numpy as np

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ld_screening.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import django
    django.setup()
except:
    pass

from assessment.ml_utils import (
    load_question_model,
    load_prediction_model,
    extract_question_features,
    extract_features
)


def test_question_model():
    """Test the question generation model."""
    print("\n" + "="*60)
    print("Testing Question Generation Model")
    print("="*60)
    
    # Load model
    model = load_question_model()
    print(f"Model type: {type(model).__name__}")
    
    # Test features
    test_features = np.array([[
        1,      # last_correct (correct)
        850,    # last_response_time (850ms)
        0,      # last_difficulty_easy
        1,      # last_difficulty_medium
        0,      # last_difficulty_hard
        0.75,   # session_accuracy (75%)
        3,      # domain_reading_count
        2,      # domain_writing_count
        2,      # domain_math_count
        1       # domain_attention_count
    ]])
    
    print(f"\nInput features shape: {test_features.shape}")
    print(f"Input features:\n{test_features}")
    
    # Get prediction
    prediction = model.predict(test_features)
    print(f"\nOutput shape: {prediction.shape}")
    print(f"Output: {prediction}")
    
    # Interpret output
    if len(prediction.shape) == 2:
        domain_idx = int(prediction[0][0])
        difficulty_idx = int(prediction[0][1])
    else:
        domain_idx = int(prediction[0])
        difficulty_idx = int(prediction[1])
    
    domains = ['reading', 'writing', 'math', 'attention']
    difficulties = ['easy', 'medium', 'hard']
    
    domain = domains[domain_idx] if 0 <= domain_idx < 4 else 'unknown'
    difficulty = difficulties[difficulty_idx] if 0 <= difficulty_idx < 3 else 'unknown'
    
    print(f"\nInterpreted result:")
    print(f"  Domain: {domain}")
    print(f"  Difficulty: {difficulty}")
    
    # Validation
    if domain in domains and difficulty in difficulties:
        print("\n✅ Question model test PASSED")
        return True
    else:
        print("\n❌ Question model test FAILED - Invalid output")
        return False


def test_prediction_model():
    """Test the final prediction model."""
    print("\n" + "="*60)
    print("Testing Final Prediction Model")
    print("="*60)
    
    # Load model
    model = load_prediction_model()
    print(f"Model type: {type(model).__name__}")
    
    # Test features
    test_features = np.array([[
        0.65,   # accuracy (65%)
        2200,   # avg_response_time (2200ms)
        0.35,   # error_rate (35%)
        850,    # consistency (850ms std dev)
        0.55,   # reading_accuracy (55%)
        0.70,   # math_accuracy (70%)
        3,      # letter_reversal_count
        2       # confidence_mismatch
    ]])
    
    print(f"\nInput features shape: {test_features.shape}")
    print(f"Input features:\n{test_features}")
    
    # Get prediction
    prediction = model.predict(test_features)
    print(f"\nOutput shape: {prediction.shape}")
    print(f"Output: {prediction}")
    
    # Extract risk scores
    if len(prediction.shape) == 2:
        dyslexia_risk = float(prediction[0][0])
        dyscalculia_risk = float(prediction[0][1])
        attention_risk = float(prediction[0][2])
    else:
        dyslexia_risk = float(prediction[0])
        dyscalculia_risk = float(prediction[1])
        attention_risk = float(prediction[2])
    
    print(f"\nInterpreted result:")
    print(f"  Dyslexia risk: {dyslexia_risk:.3f}")
    print(f"  Dyscalculia risk: {dyscalculia_risk:.3f}")
    print(f"  Attention risk: {attention_risk:.3f}")
    
    # Validation
    valid = all(0.0 <= score <= 1.0 for score in [dyslexia_risk, dyscalculia_risk, attention_risk])
    
    if valid:
        print("\n✅ Prediction model test PASSED")
        return True
    else:
        print("\n❌ Prediction model test FAILED - Scores out of range [0, 1]")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("ML Model Integration Test Suite")
    print("="*60)
    
    results = []
    
    # Test question model
    try:
        results.append(("Question Model", test_question_model()))
    except Exception as e:
        print(f"\n❌ Question model test ERROR: {e}")
        results.append(("Question Model", False))
    
    # Test prediction model
    try:
        results.append(("Prediction Model", test_prediction_model()))
    except Exception as e:
        print(f"\n❌ Prediction model test ERROR: {e}")
        results.append(("Prediction Model", False))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name}: {status}")
    
    all_passed = all(passed for _, passed in results)
    if all_passed:
        print("\n🎉 All tests passed! Models are ready to use.")
    else:
        print("\n⚠️  Some tests failed. Check model outputs above.")
    
    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
