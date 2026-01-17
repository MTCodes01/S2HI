from google import genai
from google.genai import types
from django.conf import settings
import json

# Configure API with modern client
client = genai.Client(api_key=settings.GEMINI_API_KEY)

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

        prompt = f"""You are an expert educational psychologist and learning specialist analyzing assessment results for a student.

{context}

Based on this data, provide:

1. A concise, encouraging summary (2-3 sentences) that gives an overall picture of the student's performance
2. 3-5 specific, actionable insights about patterns you observe in their performance
3. Personalized recommendations for each domain (reading, math, focus) that are:
   - Age-appropriate for a {age_group} year old
   - Specific to their performance level and mistakes
   - Practical and implementable by teachers/parents
   - Encouraging and constructive

Keep the tone professional but warm and supportive. Focus on growth potential and specific strategies."""

        print("📤 Sending request to Gemini...")
        
        # Call Gemini with structured output
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "summary": types.Schema(
                            type=types.Type.STRING,
                            description="Overall assessment summary in 2-3 sentences"
                        ),
                        "key_insights": types.Schema(
                            type=types.Type.ARRAY,
                            description="Array of 3-5 specific insights about student performance",
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
                        )
                    },
                    required=[
                        "summary",
                        "key_insights",
                        "reading_recommendation",
                        "math_recommendation",
                        "focus_recommendation"
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
