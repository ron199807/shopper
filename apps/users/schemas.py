from drf_spectacular.utils import OpenApiExample

LOGIN_RESPONSE_EXAMPLE = {
    'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
    'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
    'user': {
        'id': 1,
        'email': 'user@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'user_type': 'client',
        'phone_number': '+1234567890'
    }
}

REGISTER_REQUEST_EXAMPLE = {
    'client': {
        'email': 'client@example.com',
        'password': 'TestPass123!',
        'password2': 'TestPass123!',
        'first_name': 'John',
        'last_name': 'Client',
        'phone_number': '+1234567890',
        'user_type': 'client'
    },
    'shopper': {
        'email': 'shopper@example.com',
        'password': 'TestPass123!',
        'password2': 'TestPass123!',
        'first_name': 'Jane',
        'last_name': 'Shopper',
        'phone_number': '+0987654321',
        'user_type': 'shopper'
    }
}