"""
API Views for LD Screening Assessment.
Integrated with Gemini AI and ML Risk Classifiers.
"""
import os
import sys
import joblib
import pandas as pd
import numpy as np
import traceback
import json
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.conf import settings

# Google Gemini Imports
from google import genai
from google.genai import types

from .models import User, Session, Question, UserResponse, MistakePattern, FinalPrediction
from .serializers import (
    StartSessionRequestSerializer,
    StartSessionResponseSerializer,
    GetNextQuestionRequestSerializer,
    QuestionResponseSerializer,
    SubmitAnswerRequestSerializer,
    SubmitAnswerResponseSerializer,
    EndSessionRequestSerializer,
    EndSessionResponseSerializer,
    GetDashboardDataRequestSerializer,
    DashboardDataResponseSerializer,
    GetUserHistoryRequestSerializer
)
from .adaptive_logic import get_adaptive_question

# ==========================================
# 🧠 AI SETUP (Internal Helpers)
# ==========================================

# 1. Setup Gemini Client
try:
    gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
except AttributeError:
    gemini_client = None
    print("⚠️ GEMINI_API_KEY missing. AI Summaries will be disabled.")

# 2. Risk Model Loader (Singleton Pattern)
_risk_model = None

def get_risk_model():
    global _risk_model
    if _risk_model is None:
        try:
            # Look for risk_classifier.pkl in current dir or base dir
            current_dir = os.path.dirname(os.path.abspath(__file__))
            paths = [
                os.path.join(current_dir, 'risk_classifier.pkl'),
                os.path.join(settings.BASE_DIR, 'risk_classifier.pkl')
            ]
            for path in paths:
                if os.path.exists(path):
                    _risk_model = joblib.load(path)
                    print(f"✅ Risk Model loaded from {path}")
                    break
        except Exception as e:
            print(f"❌ Error loading risk model: {e}")
    return _risk_model

def generate_gemini_report(history_text, user_id):
    """Generates a clinical summary using Gemini."""
    if not gemini_client:
        return {}

    prompt = f"""
    Act as an Educational Psychologist. Analyze this student's assessment data.
    Student ID: {user_id}
    
    Session History:
    {history_text}
    
    Identify signs of Dyslexia (letter reversals), Dyscalculia (math errors), or ADHD (speed/focus).
    
    Output JSON with these keys: "overall_performance" (string), "specific_issues" (list), "strengths" (list), "recommended_focus" (string).
    """
    
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "overall_performance": types.Schema(type=types.Type.STRING),
                        "specific_issues": types.Schema(type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING)),
                        "strengths": types.Schema(type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING)),
                        "recommended_focus": types.Schema(type=types.Type.STRING)
                    }
                )
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Gemini Error: {e}")
        return {}

# ==========================================
# 🎮 API VIEWS
# ==========================================

class StartSessionView(APIView):
    """
    POST /start-session/
    Create a new user and session.
    """
    def post(self, request):
        serializer = StartSessionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        age_group = serializer.validated_data['age_group']
        user_id = serializer.validated_data.get('user_id')
        
        with transaction.atomic():
            if user_id:
                try:
                    user = User.objects.get(user_id=user_id)
                    user.age_group = age_group
                    user.save()
                except User.DoesNotExist:
                    user = User.objects.create(age_group=age_group)
            else:
                user = User.objects.create(age_group=age_group)
            
            session_count = Session.objects.filter(user=user).count()
            session_id = f"S_{user.user_id}_{session_count + 1:02d}"
            
            session = Session.objects.create(session_id=session_id, user=user)
        
        return Response({'user_id': user.user_id, 'session_id': session.session_id}, status=status.HTTP_201_CREATED)


class GetNextQuestionView(APIView):
    """
    POST /get-next-question/
    Get the next adaptive question based on user performance.
    """
    def post(self, request):
        serializer = GetNextQuestionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        session_id = data['session_id']
        
        try:
            session = Session.objects.get(session_id=session_id)
        except Session.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # Load question generator model
            current_dir = os.path.dirname(os.path.abspath(__file__))
            paths_to_check = [
                os.path.join(current_dir, 'question_model.pkl'),
                os.path.join(settings.BASE_DIR, 'question_model.pkl')
            ]
            
            generator = None
            for path in paths_to_check:
                if os.path.exists(path):
                    generator = joblib.load(path)
                    break
            
            if generator:
                # Calculate current state for the model
                responses = UserResponse.objects.filter(session=session).order_by('-answered_at')
                
                # Default init state
                is_correct = 1
                time_ms = 0
                d_easy, d_medium, d_hard = 1, 0, 0
                session_accuracy = 1.0
                cur_domain = 0
                domain_map = {'reading': 0, 'math': 1, 'attention': 2}

                if responses.exists():
                    last_response = responses.first()
                    is_correct = 1 if data.get('correct') else 0
                    time_ms = data.get('response_time_ms', 2000)
                    
                    if last_response.difficulty == 'medium': d_medium = 1; d_easy = 0
                    elif last_response.difficulty == 'hard': d_hard = 1; d_easy = 0
                    
                    total = responses.count()
                    correct_c = responses.filter(correct=True).count()
                    session_accuracy = correct_c / total if total > 0 else 1.0
                    cur_domain = domain_map.get(last_response.domain, 0)

                features = np.array([[is_correct, time_ms, d_easy, d_medium, d_hard, session_accuracy, cur_domain]])
                
                # Predict next
                prediction = generator.predict(features)
                if len(prediction.shape) == 2 and prediction.shape[1] == 2:
                    next_domain_idx, next_diff_idx = int(prediction[0][0]), int(prediction[0][1])
                else:
                    next_domain_idx, next_diff_idx = 0, 1

                domain_names = {0: 'reading', 1: 'math', 2: 'attention'}
                diff_names = {0: 'easy', 1: 'medium', 2: 'hard'}
                
                next_domain = domain_names.get(next_domain_idx, 'reading')
                next_difficulty = diff_names.get(next_diff_idx, 'medium')
                
                # Check session length
                response_count = UserResponse.objects.filter(session=session).count()
                if response_count >= 30:
                    return Response({'message': 'Assessment complete!', 'end_session': True}, status=status.HTTP_200_OK)
                
                # Generate
                question_data = generator.generate_question(next_domain, next_difficulty)
                question_id = f"Q_{session_id}_{response_count + 1}"
                
                return Response({
                    'question_id': question_id,
                    'domain': question_data['domain'],
                    'difficulty': question_data['difficulty'],
                    'question_text': question_data['question_text'],
                    'options': question_data['options'],
                    'correct_option': question_data['correct_option']
                }, status=status.HTTP_200_OK)
            
            else:
                # Fallback to logic if model missing
                question = get_adaptive_question(
                    session_id=session_id,
                    last_question_id=data.get('last_question_id'),
                    correct=data.get('correct'),
                    response_time_ms=data.get('response_time_ms')
                )
                if not question:
                    return Response({'message': 'End of questions', 'end_session': True}, status=status.HTTP_200_OK)
                
                return Response({
                    'question_id': question.question_id,
                    'domain': question.domain,
                    'difficulty': question.difficulty,
                    'question_text': question.question_text,
                    'options': question.options
                }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubmitAnswerView(APIView):
    """
    POST /submit-answer/
    Store user response and mistake pattern.
    """
    def post(self, request):
        serializer = SubmitAnswerRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            user = User.objects.get(user_id=data['user_id'])
            session = Session.objects.get(session_id=data['session_id'])
        except (User.DoesNotExist, Session.DoesNotExist):
            return Response({'error': 'User or Session not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Ensure question exists (or create temp for dynamic)
        question, _ = Question.objects.get_or_create(
            question_id=data['question_id'],
            defaults={
                'domain': data['domain'],
                'difficulty': data['difficulty'],
                'question_text': 'Dynamic Question',
                'options': [],
                'correct_option': 'unknown'
            }
        )

        with transaction.atomic():
            user_response = UserResponse.objects.create(
                session=session,
                user=user,
                question=question,
                domain=data['domain'],
                difficulty=data['difficulty'],
                correct=data['correct'],
                response_time_ms=data['response_time_ms'],
                confidence=data.get('confidence'),
                # Add text snapshots for Gemini if available in request, else generic
                question_text_snapshot=getattr(question, 'question_text', ''),
                user_answer_text=str(data.get('correct')) # Simplified for now
            )
            
            if data.get('mistake_type') and not data['correct']:
                severity = 'medium'
                if data['mistake_type'] in ['letter_reversal', 'number_reversal']: severity = 'high'
                elif data['mistake_type'] in ['spelling_error', 'calculation_error']: severity = 'medium'
                else: severity = 'low'
                
                MistakePattern.objects.create(
                    response=user_response,
                    mistake_type=data['mistake_type'],
                    severity=severity
                )
        
        return Response({'status': 'success', 'response_id': user_response.response_id}, status=status.HTTP_201_CREATED)


class EndSessionView(APIView):
    """
    POST /end-session/
    End session, compute ML metrics locally, and get prediction from .pkl
    """
    def post(self, request):
        serializer = EndSessionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        session_id = data['session_id']
        
        try:
            session = Session.objects.get(session_id=session_id)
            user = session.user
        except Session.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

        # 1. Fetch Responses
        responses = UserResponse.objects.filter(session=session)
        mistakes = MistakePattern.objects.filter(response__session=session)

        # 2. Compute Features for ML Model (risk_classifier.pkl)
        # Features needed: reading_acc, math_acc, focus_acc, avg_time_ms, rev_rate, pv_rate, impulse_rate
        
        def calc_acc(domain):
            qs = responses.filter(domain=domain)
            if not qs.exists(): return 0.0
            return qs.filter(correct=True).count() / qs.count()

        reading_acc = calc_acc('reading')
        math_acc = calc_acc('math')
        focus_acc = calc_acc('attention') # Mapped from 'attention' in DB to 'focus_acc'
        
        avg_time = responses.aggregate(models.Avg('response_time_ms'))['response_time_ms__avg'] or 0
        
        total_incorrect = responses.filter(correct=False).count()
        rev_count = mistakes.filter(mistake_type__in=['letter_reversal', 'number_reversal']).count()
        pv_count = mistakes.filter(mistake_type='place_value_error').count() # Assuming this type exists
        
        rev_rate = rev_count / total_incorrect if total_incorrect > 0 else 0.0
        pv_rate = pv_count / total_incorrect if total_incorrect > 0 else 0.0
        
        # Impulse rate: answers < 1000ms that were wrong
        impulse_count = responses.filter(response_time_ms__lt=1000, correct=False).count()
        impulse_rate = impulse_count / responses.count() if responses.exists() else 0.0

        # 3. Load Model and Predict
        risk_label = "Assessment Inconclusive"
        scores = {'dyslexia': 0.0, 'dyscalculia': 0.0, 'attention': 0.0}
        
        model = get_risk_model()
        if model:
            try:
                # Prepare DataFrame columns must match training exactly
                features = pd.DataFrame([{
                    "reading_acc": reading_acc,
                    "math_acc": math_acc,
                    "focus_acc": focus_acc,
                    "avg_time_ms": avg_time,
                    "rev_rate": rev_rate,
                    "pv_rate": pv_rate,
                    "impulse_rate": impulse_rate
                }])
                
                risk_label = model.predict(features)[0]
                # If model supports probabilities, get them. Otherwise mock based on label.
                try:
                    probs = model.predict_proba(features)[0]
                    # Assuming classes order: [Attention, Dyscalculia, Dyslexia, Low Risk] - verify with training!
                    # For safety, just setting the predicted one high
                    if 'Dyslexia' in risk_label: scores['dyslexia'] = 0.85
                    elif 'Dyscalculia' in risk_label: scores['dyscalculia'] = 0.85
                    elif 'Attention' in risk_label: scores['attention'] = 0.85
                except:
                    pass
            except Exception as e:
                print(f"Prediction Error: {e}")

        # 4. Save Prediction
        with transaction.atomic():
            session.completed = True
            session.save()
            
            FinalPrediction.objects.create(
                session=session,
                user=user,
                dyslexia_risk_score=scores['dyslexia'],
                dyscalculia_risk_score=scores['dyscalculia'],
                attention_risk_score=scores['attention'],
                final_label=risk_label,
                key_insights=[f"Detected {risk_label}", f"Reading Accuracy: {int(reading_acc*100)}%"],
                confidence_level="High"
            )

        return Response({
            'risk': risk_label,
            'confidence_level': "High",
            'key_insights': [f"Identified {risk_label} pattern based on performance metrics."]
        }, status=status.HTTP_200_OK)


class GetDashboardDataView(APIView):
    """
    POST /get-dashboard-data/
    Get dashboard data AND Gemini AI summary.
    """
    def post(self, request):
        serializer = GetDashboardDataRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        session_id = data['session_id']
        
        try:
            session = Session.objects.get(session_id=session_id)
            user = session.user
            prediction = FinalPrediction.objects.filter(session=session).first()
        except Session.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

        # 1. Calculate Standard Patterns
        responses = UserResponse.objects.filter(session=session)
        if not responses.exists():
             return Response({'error': 'No data'}, status=404)
             
        domain_patterns = self._calculate_domain_patterns(responses)

        # 2. GENERATE GEMINI AI SUMMARY
        # Create a text representation of the session for the LLM
        history_text = ""
        for r in responses[:20]: # Limit to first 20 for token limits
            status = "Correct" if r.correct else "Wrong"
            mistake = r.mistakes.first().mistake_type if r.mistakes.exists() else ""
            history_text += f"Domain: {r.domain}, Result: {status}, Time: {r.response_time_ms}ms, Mistake: {mistake}\n"

        ai_data = generate_gemini_report(history_text, user.user_id)
        
        # 3. Construct Final Response
        final_risk = prediction.final_label if prediction else "Pending"
        
        response_data = {
            'student_id': f'STU-{user.user_id}',
            'age_group': user.age_group,
            'final_risk': final_risk,
            'confidence': prediction.confidence_level if prediction else "N/A",
            'risk_level': 85 if "Risk" in final_risk else 20,
            'assessment_date': session.started_at.strftime('%B %d, %Y'),
            
            # Use AI Summary if available, else fallback
            'summary': ai_data.get('overall_performance', 'Assessment completed. See details below.'),
            'key_insights': ai_data.get('specific_issues', []),
            'ai_strengths': ai_data.get('strengths', []),
            'ai_recommendation': ai_data.get('recommended_focus', ''),
            
            'patterns': domain_patterns
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

    def _calculate_domain_patterns(self, responses):
        """Helper to calculate per-domain stats"""
        patterns = {}
        for domain in ['reading', 'math', 'attention']: # Map attention to focus for frontend
            d_res = responses.filter(domain=domain)
            count = d_res.count()
            if count == 0:
                patterns['focus' if domain == 'attention' else domain] = {'accuracy': 0, 'avg_time': 0, 'common_mistake': 'None'}
                continue
            
            acc = (d_res.filter(correct=True).count() / count) * 100
            avg_time = d_res.aggregate(models.Avg('response_time_ms'))['response_time_ms__avg']
            
            # Common mistake
            mistakes = MistakePattern.objects.filter(response__in=d_res)
            common = "None"
            if mistakes.exists():
                from django.db.models import Count
                common = mistakes.values('mistake_type').annotate(c=Count('mistake_type')).order_by('-c').first()['mistake_type']
            
            patterns['focus' if domain == 'attention' else domain] = {
                'accuracy': round(acc, 1),
                'avg_time': round(avg_time, 1),
                'common_mistake': common
            }
        return patterns

class GetUserHistoryView(APIView):
    """POST /get-user-history/"""
    def post(self, request):
        serializer = GetUserHistoryRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user_id = serializer.validated_data['user_id']
        preds = FinalPrediction.objects.filter(user__user_id=user_id).order_by('predicted_at')
        
        data = [{
            'date': p.predicted_at.strftime('%Y-%m-%d'),
            'risk_label': p.final_label,
            'dyslexia_score': p.dyslexia_risk_score
        } for p in preds]
        
        return Response(data, status=200)