"""
URL patterns for assessment API endpoints.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('start-session/', views.StartSessionView.as_view(), name='start-session'),
    path('get-next-question/', views.GetNextQuestionView.as_view(), name='get-next-question'),
    path('submit-answer/', views.SubmitAnswerView.as_view(), name='submit-answer'),
    path('end-session/', views.EndSessionView.as_view(), name='end-session'),
    path('get-dashboard-data/', views.GetDashboardDataView.as_view(), name='get-dashboard-data'),
    path('get-user-history/', views.GetUserHistoryView.as_view(), name='get-user-history'),
]
