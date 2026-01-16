from google import genai
from google.genai import types
from django.conf import settings
import json
import time

# Configure API with modern client
client = genai.Client(api_key=settings.GEMINI_API_KEY)

def analyze_audio_with_gemini(audio_path, expected_text, age_group):
    """
    Uploads audio to Gemini and requests an age-specific reading assessment.
    Uses modern API with structured JSON output.
    """
    print(f"🚀 Uploading to Gemini... (Context: {age_group})")
    
    try:
        # 1. Upload File using modern API
        print(f"📁 Uploading file: {audio_path}")
        audio_file = client.files.upload(file=audio_path)
        print(f"✅ File uploaded. URI: {audio_file.uri}")
        print(f"📄 File state: {audio_file.state}")
        
        # Wait for file to become ACTIVE
        # Instead of polling with client.files.get() (which causes errors),
        # just wait a few seconds for processing to complete
        if audio_file.state != "ACTIVE":
            print("⏳ Waiting for file to become ACTIVE...")
            time.sleep(5)  # WebM files need more time to process

        # 2. Age-Adaptive Prompt
        prompt = f"""
Analyze this audio recording of a student reading aloud.

Student age group: {age_group}
Expected text: "{expected_text}"

Analyze the audio for:
1. Reading speed in words per minute
2. Accuracy score (0-100) based on pronunciation and fluency
3. Emotional state: Choose one from Confident, Anxious, Frustrated, or Neutral
4. Specific words the student struggled with
5. Overall assessment and risk flag for learning difficulties
6. Recommended solutions or next steps
"""

        print("🤖 Generating content with structured output...")
        
        # 3. Use modern API with structured JSON output
        # Try with retry logic in case file needs processing time
        # WebM files can take 20-30 seconds to process
        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash-exp",
                    contents=[prompt, audio_file],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                        "reading_speed_wpm": types.Schema(
                            type=types.Type.NUMBER,
                            description="Reading speed in words per minute"
                        ),
                        "accuracy_score": types.Schema(
                            type=types.Type.NUMBER,
                            description="Accuracy score from 0-100"
                        ),
                        "emotional_state": types.Schema(
                            type=types.Type.STRING,
                            enum=["Confident", "Anxious", "Frustrated", "Neutral"],
                            description="The emotional state of the reader"
                        ),
                        "emotional_details": types.Schema(
                            type=types.Type.STRING,
                            description="Details about the emotional state"
                        ),
                        "struggle_words": types.Schema(
                            type=types.Type.ARRAY,
                            description="List of words the student struggled with",
                            items=types.Schema(type=types.Type.STRING)
                        ),
                        "assessment_summary": types.Schema(
                            type=types.Type.STRING,
                            description="Brief summary of the reading assessment"
                        ),
                        "risk_flag": types.Schema(
                            type=types.Type.BOOLEAN,
                            description="Flag indicating potential learning difficulties"
                        ),
                        "recommended_solution": types.Schema(
                            type=types.Type.STRING,
                            description="Specific advice or next steps"
                        )
                    },
                    required=[
                        "reading_speed_wpm",
                        "accuracy_score",
                        "emotional_state",
                        "emotional_details",
                        "struggle_words",
                        "assessment_summary",
                        "risk_flag",
                        "recommended_solution"
                    ]
                )
            )
        )
                break  # Success!
            except Exception as retry_error:
                error_str = str(retry_error)
                # Check if it's a file not ready error
                if ("PROCESSING" in error_str or 
                    "not ready" in error_str.lower() or 
                    "FAILED_PRECONDITION" in error_str or
                    "not in an ACTIVE state" in error_str):
                    if attempt < max_retries - 1:
                        # Aggressive progressive wait for WebM: 5s, 8s, 12s, 18s, 25s
                        wait_time = 5 + (attempt * 3) + (attempt * attempt)
                        print(f"⏳ Attempt {attempt + 1} failed, file still processing. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                # Re-raise if it's not a processing error or we're out of retries
                raise
        
        print(f"📥 Response received")
        print(f"📄 Response text (first 500 chars): {response.text[:500]}")
        
        # 4. Parse JSON response (should already be valid JSON due to schema)
        try:
            result = json.loads(response.text)
            print("✅ JSON parsed successfully")
            
            # Ensure all required fields exist with defaults (just in case)
            result.setdefault("reading_speed_wpm", 0)
            result.setdefault("accuracy_score", 0)
            result.setdefault("emotional_state", "Neutral")
            result.setdefault("emotional_details", "")
            result.setdefault("struggle_words", [])
            result.setdefault("assessment_summary", "Reading assessed")
            result.setdefault("risk_flag", False)
            result.setdefault("recommended_solution", "Continue practicing")
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode failed: {e}")
            print(f"📄 Full response text:\n{response.text}")
            # Return a default response
            return {
                "reading_speed_wpm": 100,
                "accuracy_score": 75,
                "emotional_state": "Neutral",
                "emotional_details": "Unable to analyze audio",
                "struggle_words": [],
                "assessment_summary": "Audio analysis completed but response parsing failed",
                "risk_flag": False,
                "recommended_solution": "Please review the recording"
            }
                
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print(f"❌ Full traceback:\n{traceback.format_exc()}")
        
        # Return a safe default response
        return {
            "reading_speed_wpm": 0,
            "accuracy_score": 0,
            "emotional_state": "Neutral",
            "emotional_details": f"Error: {str(e)}",
            "struggle_words": [],
            "assessment_summary": "Analysis failed due to technical error",
            "risk_flag": False,
            "recommended_solution": "Please try again later"
        }
