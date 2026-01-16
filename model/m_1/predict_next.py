import joblib
import numpy as np

# Load the trained model once
model = joblib.load("adaptive_engine_model.pkl")

def get_next_question_config(current_domain, current_diff, is_correct, time_ms):
    """
    Call this function from the Backend API.
    Input: Current state
    Output: Dictionary with next domain and difficulty
    """
    # Prepare input array (must match training order)
    # [cur_domain, cur_diff, correct, time_ms]
    features = np.array([[current_domain, current_diff, is_correct, time_ms]])
    
    # Predict
    prediction = model.predict(features)
    
    # Parse output
    next_domain_id = prediction[0][0]
    next_diff_id = prediction[0][1]

    # Map IDs back to names for the Database Team
    domains = {0: "reading", 1: "math", 2: "focus"}
    diffs = {0: "easy", 1: "medium", 2: "hard"}

    return {
        "next_domain": domains[next_domain_id],
        "next_difficulty": diffs[next_diff_id],
        "debug_info": f"Input: {features} -> Output: {prediction}"
    }

# --- TEST RUN ---
if __name__ == "__main__":
    # Example: User is on Math (1), Medium (1), got it WRONG (0), took 12 seconds (12000ms)
    # Expectation: Should drop to Easy (0)
    result = get_next_question_config(1, 1, 0, 12000)
    print("🤖 AI Recommendation:", result)