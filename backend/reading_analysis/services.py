from google import genai
from django.conf import settings
import json
import time

# Configure API
genai.configure(api_key=settings.GEMINI_API_KEY)

def analyze_audio_with_gemini(audio_path, expected_text, age_group):
    """
    Uploads audio to Gemini and requests an age-specific Dyslexia screening.
    """
    print(f"🚀 Uploading to Gemini... (Context: {age_group})")
    
    # 1. Upload File
    audio_file = genai.upload_file(audio_path)
    
    # Wait for processing
    while audio_file.state.name == "PROCESSING":
        time.sleep(1)
        audio_file = genai.get_file(audio_file.name)

    # 2. Setup Model
    model = genai.GenerativeModel("gemini-1.5-flash")

    # 3. The "Age-Adaptive" Prompt
    prompt = f"""
    Act as a Clinical Reading Specialist.
    
    Context: A student in the age group "{age_group}" is reading the following text:
    "{expected_text}"
    
    Task: Assess their reading capability, clarity, and emotional state relative to EXPECTED standards for a {age_group}.
    
    1. Assessment:
       - Pace: Is it age-appropriate? (e.g., a 7yo reads slower than a 12yo).
       - Clarity: List specific words they struggled to decode.
       - Emotion: Detect signs of frustration, anxiety (shaky voice), or confidence.
       
    2. Solution Generation (Critical):
       - Provide 2-3 specific, age-appropriate exercises or strategies to help this specific student improve based on the errors you heard.
    
    Output STRICT JSON format only. Structure:
    {{
      "reading_speed_wpm": (integer),
      "accuracy_score": (integer 0-100),
      "emotional_state": "Confident/Anxious/Frustrated/Neutral",
      "emotional_details": "Description of vocal cues (e.g., 'Sighed heavily at difficult words')",
      "struggle_words": ["word1", "word2"],
      "assessment_summary": "A 1-sentence summary of their performance.",
      "risk_flag": (boolean, true if performance is significantly below age expectations),
      "recommended_solution": "Specific advice for this student (e.g., 'Try 'Chunking' method for multi-syllable words' or 'Practice sight words list B')."
    }}
    """

    print("🤖 Analyzing with Age Context...")
    response = model.generate_content([prompt, audio_file])
    
    # 4. Clean & Parse JSON
    try:
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except Exception as e:
        print(f"❌ JSON Parse Error: {e}")
        return None