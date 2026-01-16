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
The backend uses `ld_model.pkl` for predictions. Replace with your trained model that accepts features:
- accuracy, avg_response_time, error_rate, consistency
- reading_accuracy, math_accuracy
- letter_reversal_count, confidence_mismatch

Returns: `[dyslexia_risk, dyscalculia_risk, attention_risk]`
