from google import genai
from google.genai import types
from django.conf import settings
import json
import time
import uuid

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


def generate_reading_sentence_with_gemini(age_group, difficulty=None):
    """
    Generates age-appropriate reading sentences using Gemini API.
    
    Args:
        age_group: Age group of the student (e.g., "6-8", "9-11", "12-14", "14+")
        difficulty: Optional difficulty level ("easy", "medium", "hard")
    
    Returns:
        Dict with sentence_id, text, difficulty, and domain
    """
    print(f"🎯 Generating reading sentence for age group: {age_group}, difficulty: {difficulty}")
    
    try:
        # Age-adaptive prompts
        age_prompts = {
            "6-8": "simple vocabulary appropriate for early readers (grades 1-3), short sentences with common words",
            "9-11": "moderate vocabulary for intermediate readers (grades 4-5), sentences with some multi-syllabic words",
            "12-14": "advanced vocabulary for middle school students (grades 6-8), complex sentence structures",
            "14+": "sophisticated vocabulary for high school students, challenging sentence structures with varied complexity"
        }
        
        age_context = age_prompts.get(age_group, age_prompts["9-11"])
        
        # Difficulty-specific instructions
        difficulty_instructions = {
            "easy": "Use simple, common words with straightforward pronunciation. Keep the sentence short (8-12 words).",
            "medium": "Include some tongue-twisters or alliteration to test pronunciation. Sentence length: 12-18 words.",
            "hard": "Include challenging multi-syllabic words, complex phonetic patterns, or alliteration. Sentence length: 15-25 words."
        }
        
        difficulty_hint = difficulty_instructions.get(difficulty, difficulty_instructions["medium"])
        
        prompt = f"""
Generate a single reading sentence for a reading aloud assessment.

Student age group: {age_group}
Target difficulty: {difficulty or "medium"}

Requirements:
- Use {age_context}
- {difficulty_hint}
- The sentence should be engaging and appropriate for assessment purposes
- Include varied phonetic patterns to test reading ability
- Ensure the sentence is grammatically correct and makes sense

Generate ONE sentence suitable for reading aloud practice.
"""
        
        print("🤖 Calling Gemini to generate sentence...")
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "sentence": types.Schema(
                            type=types.Type.STRING,
                            description="The generated reading sentence"
                        ),
                        "estimated_difficulty": types.Schema(
                            type=types.Type.STRING,
                            enum=["easy", "medium", "hard"],
                            description="Estimated difficulty level of the sentence"
                        ),
                        "word_count": types.Schema(
                            type=types.Type.INTEGER,
                            description="Number of words in the sentence"
                        )
                    },
                    required=["sentence", "estimated_difficulty", "word_count"]
                )
            )
        )
        
        print(f"📥 Response received from Gemini")
        
        # Parse response
        result = json.loads(response.text)
        sentence_text = result.get("sentence", "The quick brown fox jumps over the lazy dog.")
        generated_difficulty = result.get("estimated_difficulty", difficulty or "medium")
        
        # Generate unique sentence ID
        sentence_id = f"GS-{uuid.uuid4().hex[:8].upper()}"
        
        print(f"✅ Generated sentence: {sentence_text}")
        
        return {
            "sentence_id": sentence_id,
            "text": sentence_text,
            "difficulty": generated_difficulty,
            "domain": "reading"
        }
        
    except Exception as e:
        print(f"❌ Error generating sentence: {e}")
        import traceback
        print(f"❌ Full traceback:\n{traceback.format_exc()}")
        
        # Fallback sentences based on age group
        fallback_sentences = {
            "6-8": [
                {"text": "The cat sat on the mat and looked at the moon.", "difficulty": "easy"},
                {"text": "Birds fly high in the bright blue sky.", "difficulty": "easy"},
            ],
            "9-11": [
                {"text": "The butterfly fluttered between the beautiful bright flowers.", "difficulty": "medium"},
                {"text": "Peter Piper picked a peck of pickled peppers.", "difficulty": "medium"},
            ],
            "12-14": [
                {"text": "The mysterious stranger appeared suddenly at the abandoned lighthouse.", "difficulty": "hard"},
                {"text": "Scientific discoveries revolutionize our understanding of the universe.", "difficulty": "hard"},
            ],
            "14+": [
                {"text": "The philosophical implications of artificial intelligence challenge our fundamental understanding of consciousness.", "difficulty": "hard"},
                {"text": "Contemporary literature encompasses diverse perspectives and experimental narrative techniques.", "difficulty": "hard"},
            ]
        }
        
        # Select fallback based on age group
        import random
        age_fallbacks = fallback_sentences.get(age_group, fallback_sentences["9-11"])
        fallback = random.choice(age_fallbacks)
        
        return {
            "sentence_id": f"FB-{uuid.uuid4().hex[:8].upper()}",
            "text": fallback["text"],
            "difficulty": fallback["difficulty"],
            "domain": "reading"
        }
