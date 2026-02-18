"""
Main URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# API URL patterns
api_patterns = [
    # Authentication endpoints
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]

urlpatterns = [
    # Home endpoint
    path('', views.home, name='home'),
    # Admin site
    path('admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls')),
    path('api-auth/', include('rest_framework.urls')),
    
    # API root
    path('api/', include(api_patterns)),
    
    # Health check
    path('health/', lambda request: HttpResponse("OK"), name='health_check'),
]

# Serve media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Debug toolbar URLs (only in development)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns