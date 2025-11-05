from django.conf import settings
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only=True)
    
    staff_security_code = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        
        model = User
        fields = [
            'email', 'username', 'full_name', 'password',
            'phone', 'address', 'image', 'user_type', 'staff_security_code'
        ]
        
    def validate(self, attrs):
        
        user_type = attrs.get('user_type', 'USER')
        
        security_code = attrs.get('staff_security_code', None)
        
        
        if user_type == 'STAFF':
            
            if not security_code:
                
                raise serializers.ValidationError("Security code is required for staff registration.")
            
            if security_code != settings.STAFF_SECURITY_CODE:
                
                raise serializers.ValidationError("Invalid staff security code.")
        
        return attrs
    
    def create(self, validated_data):
        
        validated_data.pop('staff_security_code', None)

        user = User.objects.create_user(
            
            email=validated_data['email'],
            
            full_name=validated_data.get('full_name', ''),
            
            password=validated_data['password'],
            
            username=validated_data.get('username', ''),
            
            phone=validated_data.get('phone', ''),
            
            address=validated_data.get('address', ''),
            
            image=validated_data.get('image', None),
            
            user_type=validated_data.get('user_type', 'USER'),
        )
        return user


class LoginSerializer(serializers.Serializer):
    
    email = serializers.EmailField()
    
    password = serializers.CharField(write_only=True)
    
    staff_security_code = serializers.CharField(write_only=True, required=False)
    
    def validate(self, data):
        user = authenticate(email=data.get('email'), password=data.get('password'))
        
        if not user:
            
            raise serializers.ValidationError("Invalid email or password.")

        if user.user_type == 'STAFF':
            
            security_code = data.get('staff_security_code', None)
            
            if not security_code or security_code != settings.STAFF_SECURITY_CODE:
                
                raise serializers.ValidationError("Invalid staff security code.")
        
        data['user'] = user
        
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        
        model = User
        
        fields = ['id', 'email', 'username', 'full_name', 'phone', 'address', 'image', 'user_type']


