from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone_number', 
                 'avatar', 'bio', 'user_type', 'user_type_display', 'date_joined',
                 'average_rating', 'completed_jobs')
        read_only_fields = ('id', 'date_joined', 'average_rating', 'completed_jobs')

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    user_type = serializers.ChoiceField(choices=User.USER_TYPES, default='client')

    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'first_name', 'last_name', 
                 'phone_number', 'user_type', 'address', 'city', 'state', 'postal_code')
        
        extra_kwargs = {
            'user_type': {'required': False, 'default': 'client'},
            'address': {'required': False},
            'city': {'required': False},
            'state': {'required': False},
            'postal_code': {'required': False},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims based on user_type instead of is_seller
        token['email'] = user.email
        token['user_type'] = user.user_type
        token['is_client'] = user.user_type in ['client', 'both']
        token['is_shopper'] = user.user_type in ['shopper', 'both']
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user data to response
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'user_type': self.user.user_type,
            'phone_number': self.user.phone_number,
        }
        
        return data