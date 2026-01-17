from google import genai
from google.genai import types
from django.conf import settings
import json
import time

# Configure API with modern client
client = genai.Client(api_key=settings.GEMINI_API_KEY)

def analyze_audio_with_gemini(audio_path, expected_text, age_group):
    """
    Analyzes audio using Gemini API with inline audio data.
    No file upload needed - sends audio bytes directly.
    """
    print(f"🚀 Analyzing audio with Gemini... (Context: {age_group})")
    
    try:
        # 1. Read audio file as bytes
        print(f"📁 Reading audio file: {audio_path}")
        with open(audio_path, 'rb') as f:
            audio_bytes = f.read()
        print(f"✅ Read {len(audio_bytes)} bytes")
        
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

        print("🤖 Generating content with inline audio...")
        
        # 3. Send audio inline - no upload needed!
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[
                prompt,
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type='audio/webm'
                )
            ],
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
