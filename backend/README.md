# LD Screening Django Backend

Django REST Framework backend for Learning Disability screening with adaptive question delivery and ML-based risk assessment.

## Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure MySQL
Create a MySQL database:
```sql
CREATE DATABASE ld_screening_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Update `ld_screening/settings.py` with your MySQL credentials:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ld_screening_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 3. Run Migrations
```bash
python manage.py makemigrations assessment
python manage.py migrate
```

### 4. Load Sample Questions
```bash
python load_sample_questions.py
```

### 5. Create Placeholder ML Model (Optional)
```bash
python create_model.py
```

### 6. Create Admin User
```bash
python manage.py createsuperuser
```

### 7. Run Server
```bash
python manage.py runserver
```

Server runs at: http://127.0.0.1:8000

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/start-session/` | POST | Create user and session |
| `/get-next-question/` | POST | Get adaptive question |
| `/submit-answer/` | POST | Store response + mistake |
| `/end-session/` | POST | Get ML prediction |

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for full details.

## Project Structure
```
backend/
├── ld_screening/           # Django project
│   ├── settings.py         # Configuration
│   ├── urls.py              # Main URLs
│   └── wsgi.py
├── assessment/             # Main app
│   ├── models.py           # Database models
│   ├── views.py            # API views
│   ├── serializers.py      # Request/response serializers
│   ├── urls.py             # API URLs
│   ├── adaptive_logic.py   # Adaptive question selection
│   ├── ml_utils.py         # ML model integration
│   └── admin.py            # Admin configuration
├── manage.py
├── requirements.txt
├── API_DOCUMENTATION.md
├── create_model.py         # Generate placeholder model
└── load_sample_questions.py
```

## Database Models
- **User** - User info (age_group, created_at)
- **Session** - Assessment sessions
- **Question** - Question bank
- **UserResponse** - Individual responses
- **MistakePattern** - Error fingerprinting
- **FinalPrediction** - ML results

## ML Model Integration
The backend supports **two independent ML models**:

### 1. Question Generation Model (`question_model.pkl`)
- **Purpose**: Adaptive question selection
- **Input**: Last answer performance + session stats (10 features)
- **Output**: Next domain + difficulty
- **Fallback**: Rule-based adaptive logic

### 2. Final Prediction Model (`prediction_model.pkl`)
- **Purpose**: LD risk assessment
- **Input**: Session summary (8 features)
- **Output**: Risk scores (dyslexia, dyscalculia, attention)
- **Fallback**: Formula-based risk calculation

Both models are **optional**. Place them in the `backend/` folder to enable ML-based features.

See [MODEL_DOCUMENTATION.md](MODEL_DOCUMENTATION.md) for complete specifications.
