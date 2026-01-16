# S2HI - AI Samasya

## Project Overview
S2HI (AI Samasya) is an intelligent screening and assessment platform designed to identify learning disabilities (Dyslexia, Dyscalculia, and Attention issues) in children. The system uses a gamified React frontend to engage users and a Django backend powered by Machine Learning models to analyze performance and generate personalized question paths.

## Tech Stack
- **Frontend**: React.js, Vite
- **Backend**: Django, Django REST Framework
- **Machine Learning**: Scikit-learn (Adaptive Question Engine, Risk Classifier)
- **Database**: SQLite (Development), MySQL (Production ready)

## Architecture
- **Adaptive Engine**: Dynamically adjusts question difficulty and domain based on real-time user performance.
- **Risk Classifier**: Analyzes session data to predict risk levels for specific learning disorders.

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run migrations:
   ```bash
   python manage.py migrate
   ```
4. Start the server:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd my-react-app
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## Key Features
- **Interactive Assessment**: Gamified questions to reduce test anxiety.
- **Real-time Adaptation**: Questions get harder or easier based on answers.
- **Comprehensive Reporting**: Detailed risk analysis and insights for parents/educators.
