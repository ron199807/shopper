from django.http import JsonResponse
from django.conf import settings

def home(request):
    return JsonResponse({
        'message': 'Welcome to Shopper API',
        'version': '1.0.0',
        'environment': 'development' if settings.DEBUG else 'production',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/',
            'docs': '/api/docs/'  # If you add drf-yasg later
        }
    })