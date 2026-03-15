from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, RegisterSerializer, CustomTokenObtainPairSerializer

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, extend_schema_view
from drf_spectacular.types import OpenApiTypes

User = get_user_model()

@extend_schema_view(
    post=extend_schema(
        tags=['Authentication'],
        summary="Register a new user",
        description="Create a new user account. Users can be clients, shoppers, or both.",
        request=RegisterSerializer,
        responses={201: UserSerializer},
        examples=[
            OpenApiExample(
                'Client Registration',
                value={
                    'email': 'client@example.com',
                    'password': 'TestPass123!',
                    'password2': 'TestPass123!',
                    'first_name': 'John',
                    'last_name': 'Client',
                    'phone_number': '+1234567890',
                    'user_type': 'client'
                },
                request_only=True,
            ),
            OpenApiExample(
                'Shopper Registration',
                value={
                    'email': 'shopper@example.com',
                    'password': 'TestPass123!',
                    'password2': 'TestPass123!',
                    'first_name': 'Jane',
                    'last_name': 'Shopper',
                    'phone_number': '+0987654321',
                    'user_type': 'shopper'
                },
                request_only=True,
            ),
        ],
    )
)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

@extend_schema_view(
    get=extend_schema(
        tags=['Users'],
        summary="Get current user profile",
        description="Retrieve the profile of the currently authenticated user.",
        responses={200: UserSerializer},
    ),
    patch=extend_schema(
        tags=['Users'],
        summary="Update user profile",
        description="Update the profile of the currently authenticated user.",
        request=UserSerializer,
        responses={200: UserSerializer},
    )
)

class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_object(self):
        return self.request.user
    
@extend_schema_view(
    post=extend_schema(
        tags=['Authentication'],
        summary="Login",
        description="Obtain JWT tokens by providing email and password.",
        request=CustomTokenObtainPairSerializer,
        responses={
            200: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT
        },
        examples=[
            OpenApiExample(
                'Successful Login',
                value={
                    'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                    'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                    'user': {
                        'id': 1,
                        'email': 'user@example.com',
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'user_type': 'client'
                    }
                },
                response_only=True,
            )
        ],
    )
)    


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer