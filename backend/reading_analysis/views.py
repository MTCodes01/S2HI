from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import ReadingSession, AnalysisResult
from .services import analyze_audio_with_gemini
import traceback

class AnalyzeReadingView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        print("📥 Received Audio for Analysis...")
        
        try:
            # 1. Extract Data
            audio_file = request.FILES.get('audio')
            user_id = request.data.get('user_id', 'anon')
            expected_text = request.data.get('expected_text', "Default text")
            
            # Receive the age group from frontend
            age_group = request.data.get('age_group', '8-10 years') 
            
            print(f"📋 Request data: user_id={user_id}, age_group={age_group}")
            print(f"📋 Expected text: {expected_text[:50]}...")

            if not audio_file:
                return Response({"error": "No audio file provided"}, status=400)
            
            print(f"📁 Audio file received: {audio_file.name}, size: {audio_file.size} bytes")

            # 2. Save Session Locally
            session = ReadingSession.objects.create(
                user_id=user_id,
                session_id=f"sess_{request.data.get('session_id', '001')}",
                audio_file=audio_file,
                expected_text=expected_text
            )
            print(f"✅ Session saved: {session.session_id}")

            # 3. Call AI Service with Age Group
            print("🤖 Calling AI service...")
            ai_data = analyze_audio_with_gemini(
                session.audio_file.path, 
                expected_text,
                age_group
            )
            
            print(f"📊 AI analysis result: {ai_data}")
            
            # ai_data will always be a dict (with defaults on error), never None
            if not ai_data or not isinstance(ai_data, dict):
                print("❌ AI analysis returned invalid data")
                return Response({
                    "error": "AI analysis failed to return valid data",
                    "status": "error"
                }, status=500)

            # 4. Save Results to DB
            try:
                AnalysisResult.objects.create(
                    session=session,
                    transcribed_text=ai_data.get('assessment_summary', ''),
                    accuracy_score=ai_data.get('accuracy_score', 0),
                    wpm=ai_data.get('reading_speed_wpm', 0),
                    mispronunciations=ai_data.get('struggle_words', []),
                    risk_score="High" if ai_data.get('risk_flag') else "Low",
                    feedback=ai_data.get('recommended_solution', '')
                )
                print("✅ Results saved to database")
            except Exception as db_error:
                print(f"⚠️ Database save failed (non-critical): {db_error}")
                # Continue anyway - the analysis is still valid

            # 5. Return JSON to Frontend
            return Response({
                "status": "success",
                "analysis": ai_data
            })

        except Exception as e:
            print(f"❌ Server Error: {e}")
            print(f"❌ Full traceback:\n{traceback.format_exc()}")
            return Response({
                "error": str(e),
                "status": "error"
            }, status=500)
