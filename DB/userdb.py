import mysql.connector

# ---------------- DB CONNECTION ----------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="nandu",
    database="S2PHI"
)

cursor = db.cursor()

# ---------------- TABLE CREATION ----------------

# users
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    age_group VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# sessions
cursor.execute("""
CREATE TABLE IF NOT EXISTS sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
""")

# questions
cursor.execute("""
CREATE TABLE IF NOT EXISTS questions (
    question_id INT AUTO_INCREMENT PRIMARY KEY,
    domain VARCHAR(10),
    difficulty VARCHAR(10),
    question_text TEXT,
    correct_option VARCHAR(5),
    options JSON
)
""")

# user_responses
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_responses (
    response_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT,
    user_id INT,
    question_id INT,
    domain VARCHAR(10),
    difficulty VARCHAR(10),
    correct BOOLEAN,
    response_time_ms INT,
    confidence VARCHAR(10),
    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (question_id) REFERENCES questions(question_id)
)
""")

# mistake_patterns
cursor.execute("""
CREATE TABLE IF NOT EXISTS mistake_patterns (
    mistake_id INT AUTO_INCREMENT PRIMARY KEY,
    response_id INT,
    mistake_type VARCHAR(50),
    severity VARCHAR(10),
    FOREIGN KEY (response_id) REFERENCES user_responses(response_id)
)
""")

# final_predictions
cursor.execute("""
CREATE TABLE IF NOT EXISTS final_predictions (
    prediction_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT,
    user_id INT,
    dyslexia_risk FLOAT,
    dyscalculia_risk FLOAT,
    attention_risk FLOAT,
    final_label VARCHAR(25),
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
""")

db.commit()

# ---------------- HELPER FUNCTIONS ----------------

def create_user(age_group):
    cursor.execute(
        "INSERT INTO users (age_group) VALUES (%s)",
        (age_group,)
    )
    db.commit()
    return cursor.lastrowid


def start_session(user_id):
    cursor.execute(
        "INSERT INTO sessions (user_id) VALUES (%s)",
        (user_id,)
    )
    db.commit()
    return cursor.lastrowid


def end_session(session_id):
    cursor.execute(
        "UPDATE sessions SET completed = TRUE WHERE session_id = %s",
        (session_id,)
    )
    db.commit()


def get_question(domain, difficulty):
    cursor.execute("""
        SELECT question_id, question_text, options
        FROM questions
        WHERE domain=%s AND difficulty=%s
        ORDER BY RAND()
        LIMIT 1
    """, (domain, difficulty))
    return cursor.fetchone()

    
def store_mistake(response_id, mistake_type, severity):
    cursor.execute(
        """
        INSERT INTO mistake_patterns
        (response_id, mistake_type, severity)
        VALUES (%s,%s,%s)
        """,
        (response_id, mistake_type, severity)
    )
    db.commit()



def store_response(session_id, user_id, question_id,
                   domain, difficulty, correct,
                   response_time_ms, confidence):
    cursor.execute("""
        INSERT INTO user_responses
        (session_id, user_id, question_id,
         domain, difficulty, correct,
         response_time_ms, confidence)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (session_id, user_id, question_id,
          domain, difficulty, correct,
          response_time_ms, confidence))
    db.commit()
    return cursor.lastrowid


def store_mistake(response_id, mistake_type, severity):
    cursor.execute("""
        INSERT INTO mistake_patterns
        (response_id, mistake_type, severity)
        VALUES (%s,%s,%s)
    """, (response_id, mistake_type, severity))
    db.commit()


def store_prediction(session_id, user_id,
                     dyslexia, dyscalculia,
                     attention, label):
    cursor.execute("""
        INSERT INTO final_predictions
        (session_id, user_id,
         dyslexia_risk, dyscalculia_risk,
         attention_risk, final_label)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (session_id, user_id,
          dyslexia, dyscalculia,
          attention, label))
    db.commit()

# ---------------- TEST RUN ----------------
if __name__ == "__main__":
    user_id = create_user("9-11")
    session_id = start_session(user_id)

    q = get_question("reading", "medium")
    if q:
        qid, qtext, options = q
        response_id = store_response(
            session_id, user_id, qid,
            "reading", "medium",
            False, 1200, "low"
        )

        store_mistake(
            response_id,
            "letter_reversal",
            "high"
        )

    store_prediction(
        session_id, user_id,
        0.72, 0.18, 0.22,
        "dyslexia-risk"
    )

    end_session(session_id)

    print("✅ Final DB flow completed successfully")
