"""
Serializers for assessment API endpoints.
Updated to include AI Dashboard fields.
"""
from rest_framework import serializers

# ==========================================
# 1. START SESSION
# ==========================================
class StartSessionRequestSerializer(serializers.Serializer):
    """Request serializer for starting a new session."""
    age_group = serializers.CharField(max_length=20, default="8-10")
    user_id = serializers.IntegerField(required=False, allow_null=True)


class StartSessionResponseSerializer(serializers.Serializer):
    """Response serializer for session start."""
    user_id = serializers.IntegerField()
    session_id = serializers.CharField()


# ==========================================
# 2. GET NEXT QUESTION
# ==========================================
class GetNextQuestionRequestSerializer(serializers.Serializer):
    """Request serializer for getting next question."""
    session_id = serializers.CharField()
    # User ID is optional here as session_id is unique enough, but good for validation
    user_id = serializers.IntegerField(required=False) 
    last_question_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    correct = serializers.BooleanField(required=False, allow_null=True)
    response_time_ms = serializers.IntegerField(required=False, allow_null=True)


class QuestionResponseSerializer(serializers.Serializer):
    """Response serializer for question data."""
    question_id = serializers.CharField()
    domain = serializers.CharField()
    difficulty = serializers.CharField()
    question_text = serializers.CharField()
    options = serializers.ListField(child=serializers.CharField())
    correct_option = serializers.CharField(required=False) # Helper for frontend testing


# ==========================================
# 3. SUBMIT ANSWER
# ==========================================
class SubmitAnswerRequestSerializer(serializers.Serializer):
    """Request serializer for submitting an answer."""
    user_id = serializers.IntegerField()
    session_id = serializers.CharField()
    question_id = serializers.CharField()
    domain = serializers.CharField()
    difficulty = serializers.CharField()
    correct = serializers.BooleanField()
    response_time_ms = serializers.IntegerField()
    confidence = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    mistake_type = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class SubmitAnswerResponseSerializer(serializers.Serializer):
    """Response serializer for answer submission."""
    status = serializers.CharField()
    response_id = serializers.IntegerField()


# ==========================================
# 4. END SESSION
# ==========================================
class EndSessionRequestSerializer(serializers.Serializer):
    """Request serializer for ending a session."""
    user_id = serializers.IntegerField()
    session_id = serializers.CharField()
    confidence_level = serializers.CharField(required=False, allow_null=True)


class EndSessionResponseSerializer(serializers.Serializer):
    """Response serializer for session end with prediction."""
    risk = serializers.CharField()
    confidence_level = serializers.CharField()
    key_insights = serializers.ListField(child=serializers.CharField())


# ==========================================
# 5. DASHBOARD & HISTORY
# ==========================================
class GetUserHistoryRequestSerializer(serializers.Serializer):
    """Request serializer for getting user history."""
    user_id = serializers.IntegerField()


class GetDashboardDataRequestSerializer(serializers.Serializer):
    """Request serializer for getting dashboard data."""
    user_id = serializers.IntegerField()
    session_id = serializers.CharField()


class DomainPerformanceSerializer(serializers.Serializer):
    """Serializer for domain-specific performance metrics."""
    accuracy = serializers.FloatField()
    avg_time = serializers.FloatField()
    common_mistake = serializers.CharField()
    recommendation = serializers.CharField()


class DashboardDataResponseSerializer(serializers.Serializer):
    """
    Response serializer for dashboard data.
    UPDATED: Includes AI-generated fields.
    """
    student_id = serializers.CharField()
    age_group = serializers.CharField()
    final_risk = serializers.CharField()
    confidence = serializers.CharField()
    risk_level = serializers.FloatField()
    assessment_date = serializers.CharField()
    
    # AI Summary Fields
    summary = serializers.CharField()
    key_insights = serializers.ListField(child=serializers.CharField())
    ai_strengths = serializers.ListField(child=serializers.CharField(), required=False)
    ai_recommendation = serializers.CharField(required=False, allow_blank=True)
    
    # Nested patterns
    patterns = serializers.DictField(child=DomainPerformanceSerializer())