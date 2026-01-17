"""
URL patterns for reading analysis API endpoints.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('analyze-reading/', views.AnalyzeReadingView.as_view(), name='analyze-reading'),
]
