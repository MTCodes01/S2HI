from google import genai
from google.genai import types
from django.conf import settings
import json

# Lazy client initialization - only create when needed
_client = None

def get_client():
    """Get or create the Gemini API client"""
    global _client
    if _client is None:
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured in settings")
        _client = genai.Client(api_key=api_key)
    return _client

def generate_dashboard_insights(age_group, domain_patterns, prediction_data, total_questions):
    """
    Uses Gemini AI to generate personalized dashboard insights.
    
    Args:
        age_group: Student's age group (e.g., "6-8", "9-11", "12-14")
        domain_patterns: Dict containing performance metrics for reading, math, and focus
        prediction_data: Dict with final_label, confidence_level, and risk scores
        total_questions: Total number of questions answered
    
    Returns:
        Dict with AI-generated summary, key_insights, and domain-specific recommendations
    """
    print(f"🤖 Generating dashboard insights with Gemini for age group: {age_group}")
    
    try:
        # Prepare context for Gemini
        context = f"""
Student Profile:
- Age Group: {age_group}
- Total Questions Answered: {total_questions}
- Risk Classification: {prediction_data.get('final_label', 'N/A')}
- Confidence Level: {prediction_data.get('confidence_level', 'N/A')}

Performance Metrics:

Reading Domain:
- Accuracy: {domain_patterns['reading']['accuracy']}%
- Average Response Time: {domain_patterns['reading']['avg_time']}ms
- Common Mistake: {domain_patterns['reading']['common_mistake']}

Math Domain:
- Accuracy: {domain_patterns['math']['accuracy']}%
- Average Response Time: {domain_patterns['math']['avg_time']}ms
- Common Mistake: {domain_patterns['math']['common_mistake']}

Focus Domain:
- Accuracy: {domain_patterns['focus']['accuracy']}%
- Average Response Time: {domain_patterns['focus']['avg_time']}ms
- Common Mistake: {domain_patterns['focus']['common_mistake']}
"""

        prompt = f"""You are a learning specialist analyzing assessment results for a student.

{context}

Provide CONCISE feedback:

1. Summary: 1-2 sentences highlighting overall performance
2. Key insights: 3 brief, specific observations (one sentence each)
3. Recommendations: For each domain, provide ONE practical strategy (max 20 words) that is:
   - Age-appropriate for {age_group} year old
   - Specific to their performance
   - Actionable by teachers/parents
4. Next steps: 3 specific action items for teachers/parents (max 15 words each)

Keep responses brief and focused."""

        print("📤 Sending request to Gemini...")
        
        # Call Gemini with structured output
        response = get_client().models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "summary": types.Schema(
                            type=types.Type.STRING,
                            description="Overall assessment summary in 1-2 sentences"
                        ),
                        "key_insights": types.Schema(
                            type=types.Type.ARRAY,
                            description="Array of 3 specific insights about student performance",
                            items=types.Schema(type=types.Type.STRING)
                        ),
                        "reading_recommendation": types.Schema(
                            type=types.Type.STRING,
                            description="Personalized recommendation for reading domain"
                        ),
                        "math_recommendation": types.Schema(
                            type=types.Type.STRING,
                            description="Personalized recommendation for math domain"
                        ),
                        "focus_recommendation": types.Schema(
                            type=types.Type.STRING,
                            description="Personalized recommendation for focus domain"
                        ),
                        "next_steps": types.Schema(
                            type=types.Type.ARRAY,
                            description="Array of 3 specific action items for teachers/parents",
                            items=types.Schema(type=types.Type.STRING)
                        )
                    },
                    required=[
                        "summary",
                        "key_insights",
                        "reading_recommendation",
                        "math_recommendation",
                        "focus_recommendation",
                        "next_steps"
                    ]
                )
            )
        )
        
        print("📥 Response received from Gemini")
        
        # Parse JSON response
        try:
            result = json.loads(response.text)
            print("✅ Successfully parsed Gemini response")
            
            # Ensure all required fields exist
            result.setdefault("summary", "Assessment completed successfully.")
            result.setdefault("key_insights", [])
            result.setdefault("reading_recommendation", "Continue current learning approach.")
            result.setdefault("math_recommendation", "Continue current learning approach.")
            result.setdefault("focus_recommendation", "Continue current learning approach.")
            result.setdefault("next_steps", [])
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode failed: {e}")
            print(f"📄 Response text: {response.text[:500]}")
            raise
            
    except Exception as e:
        print(f"❌ Error generating insights: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print(f"❌ Full traceback:\n{traceback.format_exc()}")
        
        # Return None to trigger fallback logic in views
        return None
