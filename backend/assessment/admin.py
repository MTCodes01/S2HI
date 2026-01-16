from django.contrib import admin
from .models import User, Session, Question, UserResponse, MistakePattern, FinalPrediction


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'age_group', 'created_at')
    list_filter = ('age_group',)
    search_fields = ('user_id',)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'user', 'started_at', 'completed')
    list_filter = ('completed',)
    search_fields = ('session_id',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_id', 'domain', 'difficulty', 'question_text')
    list_filter = ('domain', 'difficulty')
    search_fields = ('question_id', 'question_text')


@admin.register(UserResponse)
class UserResponseAdmin(admin.ModelAdmin):
    list_display = ('response_id', 'session', 'user', 'question', 'correct', 'response_time_ms')
    list_filter = ('correct', 'domain', 'difficulty')
    search_fields = ('session__session_id',)


@admin.register(MistakePattern)
class MistakePatternAdmin(admin.ModelAdmin):
    list_display = ('mistake_id', 'response', 'mistake_type', 'severity')
    list_filter = ('mistake_type', 'severity')


@admin.register(FinalPrediction)
class FinalPredictionAdmin(admin.ModelAdmin):
    list_display = ('prediction_id', 'session', 'final_label', 'confidence_level', 'predicted_at')
    list_filter = ('final_label', 'confidence_level')
    search_fields = ('session__session_id',)
