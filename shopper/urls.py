from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from . import views
from apps.bids import views as bids_views
from apps.lists import views as lists_views
from apps.reviews import views as reviews_views
from apps.transactions import views as transactions_views
from apps.users import views as users_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import (
    SpectacularAPIView, 
    SpectacularSwaggerView, 
    SpectacularRedocView
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
    # App-specific API endpoints
    path('api/lists/', include('apps.lists.urls')),
    path('api/bids/', include('apps.bids.urls')),
    
    # Health check
    path('health/', lambda request: HttpResponse("OK"), name='health_check'),

    # API schema and documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Debug toolbar URLs (only in development)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns