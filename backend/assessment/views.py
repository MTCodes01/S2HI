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
    GetDashboardDataRequestSerializer,
    DashboardDataResponseSerializer,
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
        
        # Get next adaptive question using ML model
        try:
            import joblib
            import os
            import numpy as np
            from django.conf import settings
            
            # Load question generator model (trained by team)
            generator_path = os.path.join(settings.BASE_DIR, 'question_generator.pkl')
            
            if os.path.exists(generator_path):
                generator = joblib.load(generator_path)
                
                # Get previous responses to determine current state
                responses = UserResponse.objects.filter(session=session).order_by('-answered_at')
                
                if responses.exists():
                    last_response = responses.first()
                    # Map domain names to IDs
                    domain_map = {'reading': 0, 'writing': 0, 'math': 1, 'attention': 2, 'focus': 2}
                    diff_map = {'easy': 0, 'medium': 1, 'hard': 2}
                    
                    cur_domain = domain_map.get(last_response.domain, 0)
                    cur_diff = diff_map.get(last_response.difficulty, 1)
                    is_correct = 1 if correct else 0
                    time_ms = response_time_ms or 2000
                else:
                    # First question - start with reading, easy
                    cur_domain = 0
                    cur_diff = 0
                    is_correct = 1
                    time_ms = 2000
                
                # Prepare features for model: [cur_domain, cur_diff, correct, time_ms]
                features = np.array([[cur_domain, cur_diff, is_correct, time_ms]])
                
                # Predict next domain and difficulty
                prediction = generator.predict(features)
                
                # Parse prediction (returns [[domain, difficulty]])
                if len(prediction.shape) == 2 and prediction.shape[1] == 2:
                    next_domain_idx = int(prediction[0][0])
                    next_diff_idx = int(prediction[0][1])
                else:
                    # Fallback
                    next_domain_idx = 0
                    next_diff_idx = 1
                
                # Map indices to names
                domain_names = {0: 'reading', 1: 'math', 2: 'attention'}
                diff_names = {0: 'easy', 1: 'medium', 2: 'hard'}
                
                next_domain = domain_names.get(next_domain_idx, 'reading')
                next_difficulty = diff_names.get(next_diff_idx, 'medium')
                
                # Check if session should end (15-20 questions)
                response_count = UserResponse.objects.filter(session=session).count()
                
                if response_count >= 15:
                    # End session automatically
                    return Response(
                        {
                            'message': 'Assessment complete! Generating your results...',
                            'end_session': True,
                            'total_questions': response_count
                        },
                        status=status.HTTP_200_OK
                    )
                
                # 🎯 GENERATE QUESTION DYNAMICALLY using the model
                question_data = generator.generate_question(next_domain, next_difficulty)
                
                # Create a unique question ID
                question_id = f"Q_{session_id}_{response_count + 1}"
                
                response_data = {
                    'question_id': question_id,
                    'domain': question_data['domain'],
                    'difficulty': question_data['difficulty'],
                    'question_text': question_data['question_text'],
                    'options': question_data['options'],
                    'correct_option': question_data['correct_option']  # Include for answer validation
                }
                
                return Response(response_data, status=status.HTTP_200_OK)
                
            else:
                # Fallback to database if generator not found
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
                
        except Exception as e:
            import traceback
            return Response(
                {'error': f'Question generation failed: {str(e)}', 'traceback': traceback.format_exc()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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


class GetDashboardDataView(APIView):
    """
    POST /get-dashboard-data/
    
    Get comprehensive dashboard data for a completed session.
    
    Request:
        {"user_id": 101, "session_id": "S_101_01"}
    
    Response:
        {
            "student_id": "STU-101",
            "age_group": "9-11",
            "final_risk": "Possible Dyslexia-related Risk",
            "confidence": "Moderate",
            "risk_level": 60,
            "assessment_date": "January 16, 2026",
            "summary": "Assessment completed. Review domain analysis for insights.",
            "key_insights": ["Frequent letter reversals observed"],
            "patterns": {
                "reading": {
                    "accuracy": 65.5,
                    "avg_time": 1200.5,
                    "common_mistake": "Letter Reversal (b/d)",
                    "recommendation": "Use phonics-based games..."
                },
                "math": {...},
                "focus": {...}
            }
        }
    """
    
    def post(self, request):
        serializer = GetDashboardDataRequestSerializer(data=request.data)
        
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
        
        # Get prediction if session is completed
        prediction = None
        if session.completed:
            try:
                prediction = FinalPrediction.objects.get(session=session)
            except FinalPrediction.DoesNotExist:
                pass
        
        # Fetch all responses for this session
        responses = UserResponse.objects.filter(session=session).select_related('question')
        
        if not responses.exists():
            return Response(
                {'error': 'No responses found for this session'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Calculate domain-specific metrics
        domain_patterns = self._calculate_domain_patterns(responses)
        
        # Map risk type to display name
        risk_labels = {
            'low-risk': 'Low Risk - No Significant Concerns',
            'dyslexia-risk': 'Possible Dyslexia-related Risk',
            'dyscalculia-risk': 'Possible Dyscalculia-related Risk',
            'attention-risk': 'Possible Attention-related Risk'
        }
        
        # Calculate risk percentage from confidence level
        risk_levels = {
            'low': 30,
            'moderate': 60,
            'high': 85
        }
        
        # Prepare response data
        if prediction:
            final_risk = risk_labels.get(prediction.final_label, prediction.final_label)
            confidence = prediction.confidence_level.capitalize()
            risk_level = risk_levels.get(prediction.confidence_level, 50)
            key_insights = prediction.key_insights
        else:
            final_risk = "Assessment In Progress"
            confidence = "N/A"
            risk_level = 0
            key_insights = []
        
        # Format assessment date
        from datetime import datetime
        assessment_date = session.started_at.strftime('%B %d, %Y')
        
        response_data = {
            'student_id': f'STU-{user.user_id}',
            'age_group': user.age_group,
            'final_risk': final_risk,
            'confidence': confidence,
            'risk_level': risk_level,
            'assessment_date': assessment_date,
            'summary': ' '.join(key_insights) if key_insights else 'Assessment completed. Review the domain analysis below for detailed insights.',
            'key_insights': key_insights,
            'patterns': domain_patterns
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    def _calculate_domain_patterns(self, responses):
        """Calculate performance patterns for each domain."""
        from collections import defaultdict
        
        # Group responses by domain
        domain_data = defaultdict(list)
        for response in responses:
            # Map 'writing' and 'attention' to frontend domains
            domain = response.domain
            if domain == 'writing':
                domain = 'reading'  # Combine writing with reading
            elif domain == 'attention':
                domain = 'focus'  # Map attention to focus
            
            domain_data[domain].append(response)
        
        patterns = {}
        
        # Calculate metrics for each domain
        for domain in ['reading', 'math', 'focus']:
            domain_responses = domain_data.get(domain, [])
            
            if not domain_responses:
                # Default values if no data
                patterns[domain] = {
                    'accuracy': 0,
                    'avg_time': 0,
                    'common_mistake': 'No data',
                    'recommendation': 'Complete more questions in this domain for analysis.'
                }
                continue
            
            # Calculate accuracy
            correct_count = sum(1 for r in domain_responses if r.correct)
            accuracy = (correct_count / len(domain_responses)) * 100 if domain_responses else 0
            
            # Calculate average response time
            avg_time = sum(r.response_time_ms for r in domain_responses) / len(domain_responses)
            
            # Find most common mistake
            mistakes = []
            for response in domain_responses:
                if not response.correct:
                    mistake_patterns = MistakePattern.objects.filter(response=response)
                    for mistake in mistake_patterns:
                        mistakes.append(mistake.mistake_type)
            
            common_mistake = self._get_common_mistake(mistakes, domain)
            recommendation = self._get_recommendation(domain, accuracy, avg_time, common_mistake)
            
            patterns[domain] = {
                'accuracy': round(accuracy, 1),
                'avg_time': round(avg_time, 1),
                'common_mistake': common_mistake,
                'recommendation': recommendation
            }
        
        return patterns
    
    def _get_common_mistake(self, mistakes, domain):
        """Determine the most common mistake type."""
        if not mistakes:
            return "None"
        
        from collections import Counter
        mistake_counts = Counter(mistakes)
        most_common = mistake_counts.most_common(1)[0][0]
        
        # Map mistake types to readable names
        mistake_names = {
            'letter_reversal': 'Letter Reversal (b/d, p/q)',
            'number_reversal': 'Number Reversal',
            'spelling_error': 'Spelling Errors',
            'calculation_error': 'Calculation Errors',
            'sequence_error': 'Sequence Errors',
            'omission': 'Omissions',
            'substitution': 'Substitutions'
        }
        
        return mistake_names.get(most_common, most_common.replace('_', ' ').title())
    
    def _get_recommendation(self, domain, accuracy, avg_time, common_mistake):
        """Generate personalized recommendation based on performance."""
        
        if domain == 'reading':
            if accuracy < 60:
                return "Use highlighted letters, phonics-based games, and short reading chunks. Consider multisensory learning approaches."
            elif accuracy < 75:
                return "Continue with phonics practice. Gradually increase reading complexity with guided support."
            else:
                return "Reading skills are developing well. Encourage independent reading with age-appropriate materials."
        
        elif domain == 'math':
            if accuracy < 60:
                return "Use visual aids, manipulatives, and step-by-step problem solving. Break down complex problems into smaller steps."
            elif accuracy < 75:
                return "Practice with concrete examples and visual representations. Reinforce foundational concepts."
            else:
                return "Math skills are age-appropriate. Introduce more challenging problems to maintain engagement."
        
        elif domain == 'focus':
            if accuracy < 60 or avg_time < 800:
                return "Short tasks with clear visual cues and structured breaks are helpful. Minimize distractions during work time."
            elif accuracy < 75:
                return "Use timers and checklists to improve task completion. Provide positive reinforcement for sustained attention."
            else:
                return "Attention span is within normal range. Continue with current strategies and gradually increase task duration."
        
        return "Continue current learning approach and monitor progress."


class GetUserHistoryView(APIView):
    """
    POST /get-user-history/
    
    Get assessment history for a user to track improvement.
    
    Request:
        {"user_id": 101}
        
    Response:
        [
            {
                "date": "2024-01-15",
                "dyslexia_score": 0.45,
                "dyscalculia_score": 0.20,
                "attention_score": 0.30,
                "risk_label": "moderate"
            },
            ...
        ]
    """
    
    def post(self, request):
        from .serializers import GetUserHistoryRequestSerializer
        serializer = GetUserHistoryRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user_id = serializer.validated_data['user_id']
        
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Get all completed sessions with predictions
        predictions = FinalPrediction.objects.filter(
            user=user
        ).select_related('session').order_by('predicted_at')
        
        history_data = []
        for pred in predictions:
            history_data.append({
                'date': pred.predicted_at.strftime('%Y-%m-%d'),
                'dyslexia_score': pred.dyslexia_risk_score,
                'dyscalculia_score': pred.dyscalculia_risk_score,
                'attention_score': pred.attention_risk_score,
                'risk_label': pred.final_label
            })
            
        return Response(history_data, status=status.HTTP_200_OK)
