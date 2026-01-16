# ML Model Documentation for LD Screening

This document provides complete specifications for the two ML models used in the LD screening backend.

---

## Overview

The backend supports **two independent ML models**:

| Model | File | Purpose | Endpoint |
|-------|------|---------|----------|
| **Question Generation** | `question_model.pkl` | Adaptive question selection | `/get-next-question/` |
| **Final Prediction** | `prediction_model.pkl` | LD risk assessment | `/end-session/` |

Both models are **optional**. The backend falls back to rule-based logic if models are not available.

---

## Model 1: Question Generation Model

### Purpose
Determines the **next question's domain and difficulty** based on user's performance history.

### File Location
```
backend/question_model.pkl
```

### Input Features

The model receives **10 features** per request:

| # | Feature | Type | Description | Range/Values |
|---|---------|------|-------------|--------------|
| 1 | `last_correct` | int | Was last answer correct? | 0 (wrong) or 1 (correct) |
| 2 | `last_response_time` | int | Response time in milliseconds | 0-10000+ |
| 3 | `last_difficulty_easy` | int | Last question was easy (one-hot) | 0 or 1 |
| 4 | `last_difficulty_medium` | int | Last question was medium (one-hot) | 0 or 1 |
| 5 | `last_difficulty_hard` | int | Last question was hard (one-hot) | 0 or 1 |
| 6 | `session_accuracy` | float | Overall accuracy so far | 0.0 - 1.0 |
| 7 | `domain_reading_count` | int | Reading questions answered | 0+ |
| 8 | `domain_writing_count` | int | Writing questions answered | 0+ |
| 9 | `domain_math_count` | int | Math questions answered | 0+ |
| 10 | `domain_attention_count` | int | Attention questions answered | 0+ |

**Input Shape**: `(1, 10)` - Single sample with 10 features

**Example Input**:
```python
import numpy as np

features = np.array([[
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
```

### Output Format

The model returns **2 values**:

| # | Output | Type | Description | Values |
|---|--------|------|-------------|--------|
| 1 | `domain_index` | int | Next question domain | 0=reading, 1=writing, 2=math, 3=attention |
| 2 | `difficulty_index` | int | Next question difficulty | 0=easy, 1=medium, 2=hard |

**Output Shape**: `(1, 2)` or `(2,)` - Two integers

**Example Output**:
```python
[0, 2]  # domain=0 (reading), difficulty=2 (hard)
```

### Model Interface

Your model must implement:
```python
class QuestionGenerationModel:
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Args:
            X: Input features of shape (1, 10)
        
        Returns:
            Array of shape (1, 2) or (2,) with [domain_index, difficulty_index]
        """
        # Your model logic here
        return np.array([domain_idx, difficulty_idx])
```

### Training Recommendations

- **Algorithm**: Random Forest, XGBoost, or Neural Network
- **Target**: Multi-output classification (domain + difficulty)
- **Validation**: Ensure balanced domain distribution
- **Metrics**: Accuracy per domain, difficulty progression smoothness

---

## Model 2: Final Prediction Model

### Purpose
Predicts **LD risk scores** (dyslexia, dyscalculia, attention) based on complete session data.

### File Location
```
backend/prediction_model.pkl
```

### Input Features

The model receives **8 features** summarizing the entire session:

| # | Feature | Type | Description | Range |
|---|---------|------|-------------|-------|
| 1 | `accuracy` | float | Overall accuracy rate | 0.0 - 1.0 |
| 2 | `avg_response_time` | float | Average response time (ms) | 0 - 10000+ |
| 3 | `error_rate` | float | Error rate (1 - accuracy) | 0.0 - 1.0 |
| 4 | `consistency` | float | Std dev of response times | 0 - 5000+ |
| 5 | `reading_accuracy` | float | Accuracy on reading questions | 0.0 - 1.0 |
| 6 | `math_accuracy` | float | Accuracy on math questions | 0.0 - 1.0 |
| 7 | `letter_reversal_count` | int | Count of letter reversal mistakes | 0+ |
| 8 | `confidence_mismatch` | int | Low confidence + correct OR high confidence + incorrect | 0+ |

**Input Shape**: `(1, 8)` - Single sample with 8 features

**Example Input**:
```python
import numpy as np

features = np.array([[
    0.65,   # accuracy (65%)
    2200,   # avg_response_time (2200ms)
    0.35,   # error_rate (35%)
    850,    # consistency (850ms std dev)
    0.55,   # reading_accuracy (55%)
    0.70,   # math_accuracy (70%)
    3,      # letter_reversal_count
    2       # confidence_mismatch
]])
```

### Output Format

The model returns **3 risk scores**:

| # | Output | Type | Description | Range |
|---|--------|------|-------------|-------|
| 1 | `dyslexia_risk` | float | Dyslexia risk score | 0.0 - 1.0 |
| 2 | `dyscalculia_risk` | float | Dyscalculia risk score | 0.0 - 1.0 |
| 3 | `attention_risk` | float | Attention deficit risk score | 0.0 - 1.0 |

**Output Shape**: `(1, 3)` or `(3,)` - Three floats

**Example Output**:
```python
[0.72, 0.18, 0.35]  # High dyslexia risk, low dyscalculia, moderate attention
```

### Risk Interpretation

| Score Range | Interpretation |
|-------------|----------------|
| 0.0 - 0.3 | Low risk |
| 0.3 - 0.7 | Moderate risk |
| 0.7 - 1.0 | High risk |

### Model Interface

Your model must implement:
```python
class PredictionModel:
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Args:
            X: Input features of shape (1, 8)
        
        Returns:
            Array of shape (1, 3) or (3,) with [dyslexia, dyscalculia, attention]
        """
        # Your model logic here
        return np.array([dyslexia_risk, dyscalculia_risk, attention_risk])
```

### Training Recommendations

- **Algorithm**: Random Forest, Gradient Boosting, or Neural Network
- **Target**: Multi-output regression (3 continuous values 0-1)
- **Validation**: Cross-validation with clinical data
- **Metrics**: MAE, RMSE per risk type, AUC-ROC if thresholded

---

## Integration Instructions

### 1. Save Your Models

Save using `joblib`:
```python
import joblib

# Question generation model
joblib.dump(question_model, 'question_model.pkl')

# Prediction model
joblib.dump(prediction_model, 'prediction_model.pkl')
```

### 2. Place Models in Backend

Copy model files to:
```
backend/
├── question_model.pkl    # Optional
├── prediction_model.pkl  # Optional
└── ...
```

### 3. Test Models

Run the test script:
```bash
cd backend
python test_models.py
```

### 4. Verify Integration

The backend will automatically:
- ✅ Detect available models
- ✅ Use ML models when available
- ✅ Fall back to rule-based logic if missing
- ✅ Log which models are loaded

---

## Fallback Behavior

| Scenario | Question Selection | Risk Prediction |
|----------|-------------------|-----------------|
| Both models present | ✅ ML | ✅ ML |
| Only question model | ✅ ML | ⚠️ Rule-based |
| Only prediction model | ⚠️ Rule-based | ✅ ML |
| No models | ⚠️ Rule-based | ⚠️ Rule-based |

**Rule-based fallback**:
- **Questions**: Wrong/slow → easier, Right/fast → harder
- **Prediction**: Formula-based risk calculation

---

## Example: Complete Workflow

### Question Generation
```python
# Backend extracts features from session
features = np.array([[1, 850, 0, 1, 0, 0.75, 3, 2, 2, 1]])

# Model predicts next question
prediction = question_model.predict(features)
# Output: [0, 2] → Reading, Hard

# Backend fetches question from database
question = get_question(domain='reading', difficulty='hard')
```

### Final Prediction
```python
# Backend extracts session summary
features = np.array([[0.65, 2200, 0.35, 850, 0.55, 0.70, 3, 2]])

# Model predicts risks
prediction = prediction_model.predict(features)
# Output: [0.72, 0.18, 0.35]

# Backend formats response
{
    "risk": "dyslexia-risk",
    "confidence_level": "high",
    "key_insights": [
        "Frequent letter reversals observed (3 instances)",
        "Reading accuracy below expected level (55%)"
    ]
}
```

---

## Model Validation Checklist

Before deploying your models, verify:

- [ ] Input shape matches specification
- [ ] Output shape matches specification
- [ ] Output values are in valid ranges
- [ ] Model can be loaded with `joblib.load()`
- [ ] Predictions are deterministic (same input → same output)
- [ ] Model handles edge cases (all correct, all wrong, etc.)
- [ ] File size is reasonable (< 100MB recommended)

---

## Support

For questions or issues:
1. Check model shapes match specifications
2. Verify `joblib` version compatibility
3. Test with provided example inputs
4. Review backend logs for error messages

**Backend logs location**: Console output when running `python manage.py runserver`
