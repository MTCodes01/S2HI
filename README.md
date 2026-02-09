# LEAP - AI Samasya 🧠

**An intelligent, AI-powered screening and assessment platform for early detection of learning disabilities in children.**

LEAP (AI Samasya) combines gamified assessment experiences with cutting-edge machine learning to identify potential learning disabilities including Dyslexia, Dyscalculia, and Attention Deficit disorders. The platform adapts in real-time to each child's performance, providing personalized assessments and comprehensive insights.

---

## 🎯 Key Features

### 🎮 Interactive Gamified Assessment
- **8 Specialized Assessment Games** targeting different cognitive domains
- Age-appropriate difficulty scaling (6-8, 9-11, 12-14, 14+ age groups)
- Engaging UI designed to reduce test anxiety and increase participation
- Real-time feedback and progress tracking

### 🤖 AI-Powered Adaptive Learning
- **Gemini AI Integration** for dynamic question generation
- **ACMC (Adaptive Computerized Multistage Computer)** adaptive logic
- Real-time difficulty adjustment based on performance
- Domain rotation to ensure comprehensive assessment across:
  - **Reading**: Letter recognition, word chains, reading comprehension
  - **Math**: Number sense, visual math matching, calculation
  - **Attention**: Focus guard, task switching, time estimation
  - **Writing**: Planning, sequencing, spelling

### 🎤 Reading Analysis with AI
- Audio recording and analysis of reading fluency
- Gemini AI-powered pronunciation and pace evaluation
- Structured feedback on reading performance
- Fluency scoring and improvement tracking

### 📊 Comprehensive Risk Assessment
- **Multi-dimensional Risk Classification**:
  - Dyslexia Risk
  - Dyscalculia Risk
  - Attention Risk
  - Low Risk (Normal development)
- Machine Learning-based prediction using behavioral metrics
- Rule-based fallback system for reliability
- Detailed mistake fingerprinting (letter reversals, calculation errors, etc.)

### 📈 Smart Dashboard & Reporting
- Visual performance analytics with charts and graphs
- Domain-specific insights and recommendations
- Historical progress tracking across multiple sessions
- PDF export capability for comprehensive reports
- Gemini AI-generated personalized insights and recommendations

---

## 🏗️ Architecture

### Tech Stack

**Frontend**
- **Framework**: React 19.2 with TypeScript
- **Build Tool**: Vite 7.2
- **Routing**: React Router DOM 7.12
- **Charts**: Recharts 3.6
- **PDF Generation**: jsPDF + html2canvas

**Backend**
- **Framework**: Django 4.2+ with Django REST Framework
- **Database**: SQLite (Development) / MySQL (Production-ready)
- **AI/ML**:
  - Google Gemini AI for question generation and insights
  - Scikit-learn for adaptive engine and risk classification
  - NumPy for numerical computations
  - Joblib for model persistence

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Assessment  │  │   Dashboard  │  │   Reading    │      │
│  │    Games     │  │  & Analytics │  │   Analysis   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                    RESTful API (JSON)
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Django Backend                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Gemini AI  │  │  Adaptive    │  │     Risk     │      │
│  │   Question   │  │   Logic      │  │ Classifier   │      │
│  │  Generator   │  │   Engine     │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │   Reading    │  │  Dashboard   │                        │
│  │  Analysis    │  │   Insights   │                        │
│  │  (Gemini)    │  │   (Gemini)   │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                            │
                    ┌───────┴────────┐
                    │   Database     │
                    │  (SQLite/MySQL)│
                    └────────────────┘
```

---

## 🎮 Assessment Games

1. **LetterFlipFrenzy** - Reading domain: Letter recognition and reversal detection
2. **WordChainBuilder** - Reading domain: Vocabulary and word formation
3. **NumberSenseDash** - Math domain: Number identification and comparison
4. **VisualMathMatch** - Math domain: Visual arithmetic and pattern matching
5. **FocusGuard** - Attention domain: Sustained attention and concentration
6. **TimeEstimator** - Attention domain: Time perception and estimation
7. **PlanAheadPuzzle** - Writing domain: Planning and sequencing skills
8. **ConfidenceSlider** - Meta-cognitive: Self-assessment and confidence tracking

---

## 🚀 Getting Started

### Prerequisites
- **Python**: 3.8 or higher
- **Node.js**: 16 or higher
- **Google Gemini API Key**: Required for AI features

### Backend Setup

1. **Navigate to the backend directory**
   ```bash
   cd backend
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Create a `.env` file in the `backend` directory:
   ```bash
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start the development server**
   ```bash
   python manage.py runserver
   ```

   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to the frontend directory**
   ```bash
   cd my-react-app
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173`

### First Time Setup

1. Start both backend and frontend servers
2. Open your browser to `http://localhost:5173`
3. Select an age group to begin assessment
4. Complete the assessment games
5. View comprehensive results on the dashboard

---

## 📚 Documentation

### API Documentation
Comprehensive API documentation is available at [`backend/API_DOCUMENTATION.md`](backend/API_DOCUMENTATION.md)

**Key Endpoints:**
- `POST /start-session/` - Create new assessment session
- `POST /get-next-question/` - Get adaptive next question
- `POST /submit-answer/` - Submit answer with metrics
- `POST /end-session/` - Complete session and get results
- `POST /get-dashboard-data/` - Retrieve dashboard analytics
- `POST /get-user-history/` - Get historical progress
- `POST /reading-analysis/analyze/` - Analyze reading audio

### ML Model Documentation
Detailed ML model specifications at [`backend/MODEL_DOCUMENTATION.md`](backend/MODEL_DOCUMENTATION.md)

**Models Used:**
- **Question Generator** (`question_model.pkl`): Adaptive question selection
- **Risk Classifier** (`prediction_model.pkl`): LD risk assessment

---

## 🔬 How It Works

### Adaptive Assessment Flow

1. **Session Initialization**
   - User selects age group
   - System creates user profile and session

2. **Dynamic Question Generation**
   - Gemini AI generates age-appropriate questions
   - ACMC logic determines optimal difficulty
   - Domain rotation ensures balanced assessment
   - Real-time adaptation to user performance

3. **Performance Tracking**
   - Response time monitoring
   - Accuracy tracking per domain
   - Mistake pattern fingerprinting
   - Confidence level assessment

4. **Risk Analysis**
   - ML model analyzes behavioral metrics
   - Pattern detection across domains
   - Multi-dimensional risk scoring
   - Generates actionable insights

5. **Results & Reporting**
   - Comprehensive dashboard with visualizations
   - Domain-specific performance breakdown
   - Personalized recommendations
   - Progress tracking across sessions
   - Exportable PDF reports

### Adaptive Logic (ACMC)

The system uses **Adaptive Computerized Multistage Computer** principles:

- **Correct + Fast** → Increase difficulty
- **Correct + Slow** → Maintain or slightly increase difficulty
- **Incorrect + Fast** → Decrease difficulty, possible attention issue
- **Incorrect + Slow** → Decrease difficulty, possible comprehension issue

Domain balancing ensures comprehensive assessment across all cognitive areas.

---

## 🎨 Project Structure

```
LEAP/
├── backend/                          # Django backend
│   ├── assessment/                   # Core assessment API
│   │   ├── views.py                  # API endpoints
│   │   ├── models.py                 # Database models
│   │   ├── gemini_question_service.py # AI question generation
│   │   ├── adaptive_logic.py         # ACMC adaptive logic
│   │   ├── ml_utils.py               # ML model integration
│   │   └── gemini_dashboard_service.py # AI insights
│   ├── reading_analysis/             # Reading analysis module
│   │   ├── views.py                  # Reading API
│   │   └── services.py               # Gemini audio analysis
│   ├── ld_screening/                 # Django project settings
│   ├── requirements.txt              # Python dependencies
│   ├── API_DOCUMENTATION.md          # API reference
│   └── MODEL_DOCUMENTATION.md        # ML model specs
│
├── my-react-app/                     # React frontend
│   ├── src/
│   │   ├── pages/                    # Main pages
│   │   │   ├── Assessment.tsx        # Assessment interface
│   │   │   ├── Dashboard.tsx         # Results dashboard
│   │   │   ├── ReadingAloud.tsx      # Reading analysis
│   │   │   ├── FullAssessment.tsx    # Complete flow
│   │   │   └── LandingAnimation.tsx  # Landing page
│   │   ├── games/                    # Assessment games
│   │   │   ├── LetterFlipFrenzy.tsx
│   │   │   ├── WordChainBuilder.tsx
│   │   │   ├── NumberSenseDash.tsx
│   │   │   ├── VisualMathMatch.tsx
│   │   │   ├── FocusGuard.tsx
│   │   │   ├── TimeEstimator.tsx
│   │   │   ├── PlanAheadPuzzle.tsx
│   │   │   └── ConfidenceSlider.tsx
│   │   ├── components/               # Reusable components
│   │   │   ├── AudioRecorder.tsx
│   │   │   ├── ImprovementGraph.tsx
│   │   │   ├── ReportTemplate.tsx
│   │   │   └── Navbar.tsx
│   │   ├── services/                 # API integration
│   │   ├── styles/                   # CSS modules
│   │   └── types/                    # TypeScript types
│   ├── package.json                  # Node dependencies
│   └── vite.config.ts                # Vite configuration
│
├── model/                            # ML models
│   ├── adaptive_engine_model.pkl
│   ├── risk_classifier.pkl
│   └── question_generator_model.pkl
│
└── README.md                         # This file
```

---

## 🔐 Environment Variables

### Backend `.env` Configuration

```bash
# Gemini AI API Key (Required)
GEMINI_API_KEY=your_gemini_api_key_here

# Database Configuration (Optional, defaults to SQLite)
DB_ENGINE=django.db.backends.mysql
DB_NAME=s2hi_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306

# Django Settings
DEBUG=True
SECRET_KEY=your_secret_key_here
```

### CORS Configuration

The backend accepts requests from:
- `http://localhost:5173` (Vite default)
- `http://localhost:3000` (React default)
- `http://127.0.0.1:5173`
- `http://127.0.0.1:3000`

Update `CORS_ALLOWED_ORIGINS` in `backend/ld_screening/settings.py` for production deployment.

---

## 🧪 Testing

### Running Backend Tests
```bash
cd backend
python manage.py test
```

### Running Frontend Tests
```bash
cd my-react-app
npm run test
```

---

## 📊 Risk Classification

The system evaluates multiple dimensions:

### Risk Categories
- **Low Risk**: Normal development, no significant indicators
- **Dyslexia Risk**: Reading/writing difficulties, letter reversals
- **Dyscalculia Risk**: Math processing difficulties, number confusion
- **Attention Risk**: Focus/concentration difficulties, impulsivity

### Assessment Metrics
- Overall accuracy rate
- Domain-specific performance
- Response time patterns
- Mistake fingerprinting
- Confidence calibration
- Behavioral consistency

### Confidence Levels
- **Low** (< 40%): Preliminary indicators
- **Moderate** (40-70%): Notable patterns observed
- **High** (> 70%): Strong indicators present

---

## 🎯 Roadmap

- [x] Gemini AI question generation
- [x] Adaptive difficulty engine
- [x] 8 assessment games
- [x] Reading analysis with audio
- [x] Risk classification system
- [x] Dashboard with insights
- [x] PDF export functionality
- [ ] Multi-language support
- [ ] Parent/teacher portal
- [ ] Longitudinal tracking
- [ ] Intervention recommendations
- [ ] Mobile app (iOS/Android)

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Google Gemini AI** for powering intelligent question generation and insights
- **Django & React communities** for excellent frameworks and tools
- **Clinical research** in learning disabilities for informing our assessment methodology

---

## 📞 Support

For questions, issues, or contributions:
- 📧 Email: support@LEAP.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/LEAP/issues)
- 📖 Documentation: See `/backend/API_DOCUMENTATION.md` and `/backend/MODEL_DOCUMENTATION.md`

---

## ⚠️ Important Notes

### Medical Disclaimer
LEAP is a **screening tool** designed to identify potential learning difficulties. It is **NOT a diagnostic tool**. Results should be reviewed by qualified educational psychologists or medical professionals for formal diagnosis and intervention planning.

### Privacy & Data Security
- All assessment data is stored locally by default
- No personally identifiable information is required
- Audio recordings are processed and not permanently stored unless configured
- Follow GDPR/COPPA guidelines when deploying in production

### Age Appropriateness
The system is designed for children aged 6-14+. Questions and difficulty levels are automatically adjusted based on the selected age group to ensure appropriate cognitive challenge.

---

**Built with ❤️ for early intervention in learning disabilities**
