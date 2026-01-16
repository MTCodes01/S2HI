"""
Database models for LD Screening Assessment.
"""
from django.db import models


class User(models.Model):
    """Stores user information for assessment sessions."""
    user_id = models.AutoField(primary_key=True)
    age_group = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"User {self.user_id} ({self.age_group})"


class Session(models.Model):
    """Tracks assessment sessions for each user."""
    session_id = models.CharField(max_length=50, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    started_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    class Meta:
        db_table = 'sessions'

    def __str__(self):
        return f"Session {self.session_id}"


class Question(models.Model):
    """Question bank with domain, difficulty, and options."""
    DOMAIN_CHOICES = [
        ('reading', 'Reading'),
        ('writing', 'Writing'),
        ('math', 'Math'),
        ('attention', 'Attention'),
    ]

    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    question_id = models.CharField(max_length=20, primary_key=True)
    domain = models.CharField(max_length=20, choices=DOMAIN_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    question_text = models.TextField()
    options = models.JSONField()  # List of options
    correct_option = models.CharField(max_length=255)

    class Meta:
        db_table = 'questions'

    def __str__(self):
        return f"{self.question_id}: {self.question_text[:50]}"


class UserResponse(models.Model):
    """Stores individual user responses during assessment."""
    CONFIDENCE_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    response_id = models.AutoField(primary_key=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='responses')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='responses')
    domain = models.CharField(max_length=20)
    difficulty = models.CharField(max_length=20)
    correct = models.BooleanField()
    response_time_ms = models.IntegerField()
    confidence = models.CharField(max_length=20, choices=CONFIDENCE_CHOICES, null=True, blank=True)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_responses'

    def __str__(self):
        return f"Response {self.response_id} - {'Correct' if self.correct else 'Incorrect'}"


class MistakePattern(models.Model):
    """Mistake fingerprinting for identifying learning disability patterns."""
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    mistake_id = models.AutoField(primary_key=True)
    response = models.ForeignKey(UserResponse, on_delete=models.CASCADE, related_name='mistakes')
    mistake_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')

    class Meta:
        db_table = 'mistake_patterns'

    def __str__(self):
        return f"{self.mistake_type} ({self.severity})"


class FinalPrediction(models.Model):
    """Stores ML model prediction results for completed sessions."""
    prediction_id = models.AutoField(primary_key=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='predictions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='predictions')
    dyslexia_risk_score = models.FloatField()
    dyscalculia_risk_score = models.FloatField()
    attention_risk_score = models.FloatField()
    final_label = models.CharField(max_length=100)
    key_insights = models.JSONField(null=True, blank=True)
    confidence_level = models.CharField(max_length=20, default='moderate')
    predicted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'final_predictions'

    def __str__(self):
        return f"Prediction {self.prediction_id}: {self.final_label}"
