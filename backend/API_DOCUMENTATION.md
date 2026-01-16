# LD Screening Backend API Documentation

REST API documentation for React frontend integration.

---

## Base URL
```
http://localhost:8000
```

## Headers
All requests must include:
```
Content-Type: application/json
```

---

## Endpoints

### 1. Start Session
Create a new user and assessment session.

**Endpoint:** `POST /start-session/`

**Request:**
```json
{
  "age_group": "9-11"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `age_group` | string | Yes | User's age group (e.g., "6-8", "9-11", "12-14") |

**Response (201 Created):**
```json
{
  "user_id": 101,
  "session_id": "S_101_01"
}
```

**React Example:**
```javascript
const startSession = async (ageGroup) => {
  const response = await fetch('http://localhost:8000/start-session/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ age_group: ageGroup })
  });
  return await response.json();
};
```

---

### 2. Get Next Question
Fetch the next adaptive question based on performance.

**Endpoint:** `POST /get-next-question/`

**Request:**
```json
{
  "user_id": 101,
  "session_id": "S_101_01",
  "last_question_id": "R_05",
  "correct": false,
  "response_time_ms": 980
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | integer | Yes | User ID from start-session |
| `session_id` | string | Yes | Session ID from start-session |
| `last_question_id` | string | No | ID of previous question (null for first question) |
| `correct` | boolean | No | Whether previous answer was correct |
| `response_time_ms` | integer | No | Response time in milliseconds |

**Response (200 OK):**
```json
{
  "question_id": "R_06",
  "domain": "reading",
  "difficulty": "medium",
  "question_text": "Which letter is this?",
  "options": ["b", "d", "p", "q"]
}
```

**End of Questions Response:**
```json
{
  "message": "No more questions available",
  "end_session": true
}
```

**React Example:**
```javascript
const getNextQuestion = async (userId, sessionId, lastQuestion = null) => {
  const body = {
    user_id: userId,
    session_id: sessionId,
    ...(lastQuestion && {
      last_question_id: lastQuestion.id,
      correct: lastQuestion.correct,
      response_time_ms: lastQuestion.responseTime
    })
  };
  
  const response = await fetch('http://localhost:8000/get-next-question/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  return await response.json();
};
```

---

### 3. Submit Answer
Store user response and mistake fingerprinting.

**Endpoint:** `POST /submit-answer/`

**Request:**
```json
{
  "user_id": 101,
  "session_id": "S_101_01",
  "question_id": "R_05",
  "domain": "reading",
  "difficulty": "medium",
  "correct": false,
  "response_time_ms": 980,
  "confidence": "low",
  "mistake_type": "letter_reversal"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | integer | Yes | User ID |
| `session_id` | string | Yes | Session ID |
| `question_id` | string | Yes | Question ID answered |
| `domain` | string | Yes | Question domain: reading, writing, math, attention |
| `difficulty` | string | Yes | Difficulty: easy, medium, hard |
| `correct` | boolean | Yes | Whether answer was correct |
| `response_time_ms` | integer | Yes | Time taken to answer (ms) |
| `confidence` | string | No | User confidence: low, medium, high |
| `mistake_type` | string | No | Error type: letter_reversal, number_reversal, spelling_error, etc. |

**Response (201 Created):**
```json
{
  "status": "success",
  "response_id": 1
}
```

**React Example:**
```javascript
const submitAnswer = async (response) => {
  const res = await fetch('http://localhost:8000/submit-answer/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: response.userId,
      session_id: response.sessionId,
      question_id: response.questionId,
      domain: response.domain,
      difficulty: response.difficulty,
      correct: response.correct,
      response_time_ms: response.responseTime,
      confidence: response.confidence,
      mistake_type: response.mistakeType
    })
  });
  return await res.json();
};
```

---

### 4. End Session
Complete session and get ML prediction.

**Endpoint:** `POST /end-session/`

**Request:**
```json
{
  "user_id": 101,
  "session_id": "S_101_01"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | integer | Yes | User ID |
| `session_id` | string | Yes | Session ID |

**Response (200 OK):**
```json
{
  "risk": "dyslexia-risk",
  "confidence_level": "moderate",
  "key_insights": [
    "Frequent letter reversals observed",
    "Reading speed slower than age norm"
  ]
}
```

**Possible Risk Values:**
- `low-risk` - No significant indicators
- `dyslexia-risk` - Reading/writing difficulties
- `dyscalculia-risk` - Math processing difficulties
- `attention-risk` - Attention/focus difficulties

**Confidence Levels:**
- `low` - Risk score < 0.4
- `moderate` - Risk score 0.4-0.7
- `high` - Risk score > 0.7

**React Example:**
```javascript
const endSession = async (userId, sessionId) => {
  const response = await fetch('http://localhost:8000/end-session/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      session_id: sessionId
    })
  });
  return await response.json();
};
```

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "error": "Error message description"
}
```

**Common HTTP Status Codes:**
| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input data |
| 404 | Not Found - User/Session/Question not found |
| 500 | Server Error - Internal error |

---

## Complete Flow Example

```javascript
// 1. Start session
const session = await startSession('9-11');
const { user_id, session_id } = session;

// 2. Get first question
let question = await getNextQuestion(user_id, session_id);

// 3. Answer questions in a loop
while (!question.end_session) {
  const startTime = Date.now();
  
  // User selects answer (your UI logic)
  const selectedOption = await getUserSelection(question.options);
  const isCorrect = selectedOption === correctAnswer;
  const responseTime = Date.now() - startTime;
  
  // Submit answer
  await submitAnswer({
    userId: user_id,
    sessionId: session_id,
    questionId: question.question_id,
    domain: question.domain,
    difficulty: question.difficulty,
    correct: isCorrect,
    responseTime: responseTime,
    confidence: 'medium',
    mistakeType: isCorrect ? null : 'letter_reversal'
  });
  
  // Get next question
  question = await getNextQuestion(user_id, session_id, {
    id: question.question_id,
    correct: isCorrect,
    responseTime: responseTime
  });
}

// 4. End session and get results
const results = await endSession(user_id, session_id);
console.log('Risk:', results.risk);
console.log('Insights:', results.key_insights);
```

---

## Mistake Types Reference

| Type | Description | Associated Risk |
|------|-------------|-----------------|
| `letter_reversal` | Confusing b/d, p/q | Dyslexia |
| `number_reversal` | Confusing 6/9, 2/5 | Dyscalculia |
| `spelling_error` | Incorrect spelling | Dyslexia |
| `calculation_error` | Math computation error | Dyscalculia |
| `sequence_error` | Wrong order/sequence | Attention |
| `omission` | Missing letters/numbers | Attention |
| `substitution` | Replacing with similar | Dyslexia/Dyscalculia |

---

## CORS Configuration

The backend is configured to accept requests from:
- `http://localhost:3000`
- `http://localhost:5173`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:5173`

For production, update `CORS_ALLOWED_ORIGINS` in `settings.py`.
