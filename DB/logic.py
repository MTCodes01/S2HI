from userdb import (
    get_question,
    store_response,
    store_mistake
)

# ---------------- ADAPTIVE DIFFICULTY ----------------

def next_difficulty(current, correct, response_time):
    if correct and response_time < 900:
        return "hard" if current == "medium" else "medium"

    if not correct or response_time > 1400:
        return "easy" if current == "medium" else "medium"

    return current


# ---------------- SESSION LOOP LOGIC ----------------

def handle_response(session_id, user_id,
                    question_id, domain,
                    difficulty, correct,
                    response_time, confidence,
                    mistake_type=None, severity=None):

    response_id = store_response(
        session_id, user_id, question_id,
        domain, difficulty,
        correct, response_time, confidence
    )

    if not correct and mistake_type:
        store_mistake(response_id, mistake_type, severity)

    return next_difficulty(difficulty, correct, response_time)
