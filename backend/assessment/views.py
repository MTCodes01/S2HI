"""
API Views for LD Screening Assessment.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction

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
)
from .adaptive_logic import get_adaptive_question
from .ml_utils import get_prediction


class StartSessionView(APIView):
    """
    POST /start-session/
    
    Create a new user and session.
    
    Request:
        {"age_group": "9-11"}
    
    Response:
        {"user_id": 101, "session_id": "S_101_01"}
    """
    
    def post(self, request):
        serializer = StartSessionRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        age_group = serializer.validated_data['age_group']
        
        with transaction.atomic():
            # Create new user
            user = User.objects.create(age_group=age_group)
            
            # Generate session ID
            session_count = Session.objects.filter(user=user).count()
            session_id = f"S_{user.user_id}_{session_count + 1:02d}"
            
            # Create session
            session = Session.objects.create(
                session_id=session_id,
                user=user
            )
        
        response_data = {
            'user_id': user.user_id,
            'session_id': session.session_id
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class GetNextQuestionView(APIView):
    """
    POST /get-next-question/
    
    Get the next adaptive question based on user performance.
    
    Request:
        {
            "user_id": 101,
            "session_id": "S_101_01",
            "last_question_id": "R_05",
            "correct": false,
            "response_time_ms": 980
        }
    
    Response:
        {
            "question_id": "R_06",
            "domain": "reading",
            "difficulty": "medium",
            "question_text": "Which letter is this?",
            "options": ["b", "d", "p", "q"]
        }
    """
    
    def post(self, request):
        serializer = GetNextQuestionRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        session_id = data['session_id']
        last_question_id = data.get('last_question_id')
        correct = data.get('correct')
        response_time_ms = data.get('response_time_ms')
        
        # Validate session exists
        try:
            session = Session.objects.get(session_id=session_id)
        except Session.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get next adaptive question
        question = get_adaptive_question(
            session_id=session_id,
            last_question_id=last_question_id,
            correct=correct,
            response_time_ms=response_time_ms
        )
        
        if not question:
            return Response(
                {'message': 'No more questions available', 'end_session': True},
                status=status.HTTP_200_OK
            )
        
        response_data = {
            'question_id': question.question_id,
            'domain': question.domain,
            'difficulty': question.difficulty,
            'question_text': question.question_text,
            'options': question.options
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class SubmitAnswerView(APIView):
    """
    POST /submit-answer/
    
    Store user response and mistake pattern.
    
    Request:
        {
            "user_id": 101,
            "session_id": "S_101_01",
            "question_id": "R_05",
            "domain": "reading",
            "difficulty": "medium",
            "correct": false,
            "response_time_ms": 980,
            "confidence": "low",
            "mistake_type": "letter_reversal"
        }
    
    Response:
        {"status": "success", "response_id": 1}
    """
    
    def post(self, request):
        serializer = SubmitAnswerRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Validate user, session, and question exist
        try:
            user = User.objects.get(user_id=data['user_id'])
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            session = Session.objects.get(session_id=data['session_id'])
        except Session.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            question = Question.objects.get(question_id=data['question_id'])
        except Question.DoesNotExist:
            # Create question if it doesn't exist (for testing)
            question = Question.objects.create(
                question_id=data['question_id'],
                domain=data['domain'],
                difficulty=data['difficulty'],
                question_text='Test question',
                options=['a', 'b', 'c', 'd'],
                correct_option='a'
            )
        
        with transaction.atomic():
            # Create user response
            user_response = UserResponse.objects.create(
                session=session,
                user=user,
                question=question,
                domain=data['domain'],
                difficulty=data['difficulty'],
                correct=data['correct'],
                response_time_ms=data['response_time_ms'],
                confidence=data.get('confidence')
            )
            
            # Create mistake pattern if provided and answer is incorrect
            mistake_type = data.get('mistake_type')
            if mistake_type and not data['correct']:
                # Determine severity based on mistake type
                severity = 'medium'
                if mistake_type in ['letter_reversal', 'number_reversal']:
                    severity = 'high'
                elif mistake_type in ['spelling_error', 'calculation_error']:
                    severity = 'medium'
                else:
                    severity = 'low'
                
                MistakePattern.objects.create(
                    response=user_response,
                    mistake_type=mistake_type,
                    severity=severity
                )
        
        return Response(
            {'status': 'success', 'response_id': user_response.response_id},
            status=status.HTTP_201_CREATED
        )


class EndSessionView(APIView):
    """
    POST /end-session/
    
    End session, compute features, and get ML prediction.
    
    Request:
        {"user_id": 101, "session_id": "S_101_01"}
    
    Response:
        {
            "risk": "dyslexia-risk",
            "confidence_level": "moderate",
            "key_insights": [
                "Frequent letter reversals observed",
                "Reading speed slower than age norm"
            ]
        }
    """
    
    def post(self, request):
        serializer = EndSessionRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        user_id = data['user_id']
        session_id = data['session_id']
        
        # Validate user and session
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            session = Session.objects.get(session_id=session_id)
        except Session.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Fetch all responses for this session
        responses = UserResponse.objects.filter(
            session=session
        ).select_related('question')
        
        # Convert to list of dictionaries for ML processing
        response_data = []
        for response in responses:
            # Get mistake types for this response
            mistakes = MistakePattern.objects.filter(response=response)
            mistake_type = mistakes.first().mistake_type if mistakes.exists() else None
            
            response_data.append({
                'question_id': response.question_id,
                'domain': response.domain,
                'difficulty': response.difficulty,
                'correct': response.correct,
                'response_time_ms': response.response_time_ms,
                'confidence': response.confidence,
                'mistake_type': mistake_type
            })
        
        # Get ML prediction
        prediction_result = get_prediction(response_data)
        
        with transaction.atomic():
            # Mark session as completed
            session.completed = True
            session.save()
            
            # Store prediction
            FinalPrediction.objects.create(
                session=session,
                user=user,
                dyslexia_risk_score=prediction_result['scores']['dyslexia'],
                dyscalculia_risk_score=prediction_result['scores']['dyscalculia'],
                attention_risk_score=prediction_result['scores']['attention'],
                final_label=prediction_result['risk'],
                key_insights=prediction_result['key_insights'],
                confidence_level=prediction_result['confidence_level']
            )
        
        # Return response to frontend
        return Response({
            'risk': prediction_result['risk'],
            'confidence_level': prediction_result['confidence_level'],
            'key_insights': prediction_result['key_insights']
        }, status=status.HTTP_200_OK)
