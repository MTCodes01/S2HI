"""
URL configuration for ld_screening project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/', include('assessment.urls')),
    path('api/reading/', include('reading_analysis.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
