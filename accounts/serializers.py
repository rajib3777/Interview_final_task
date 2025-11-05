from django.conf import settings
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
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
        user.is_active = False
        user.save()

        request = self.context.get('request')

        current_site = get_current_site(request)

        uid = urlsafe_base64_encode(force_bytes(user.pk))

        token = default_token_generator.make_token(user)

        activation_link = f"http://{current_site.domain}/api/accounts/activate/{uid}/{token}/"

        
        message = render_to_string('accounts/verify_email.html', {

            'user': user,

            'activation_link': activation_link,

        })

        mail = EmailMessage(

            subject='Verify your email address',

            body=message,

            from_email=settings.DEFAULT_FROM_EMAIL,

            to=[user.email],
        )

        mail.content_subtype = 'html'

        mail.send()

        
        print(f"\n📧 Verification link for {user.email}: {activation_link}\n")

        
        api_token, _ = Token.objects.get_or_create(user=user)

        
        return {
        
            "user": user,
            
            "token": api_token.key,
            
            "activation_link": activation_link
        }


class LoginSerializer(serializers.Serializer):
    
    email = serializers.EmailField()
    
    password = serializers.CharField(write_only=True)
    
    staff_security_code = serializers.CharField(write_only=True, required=False)
    
    def validate(self, data):
        user = authenticate(email=data.get('email'), password=data.get('password'))
        
        if not user:
            
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            
            raise serializers.ValidationError("Account not activated. Please verify your email.")

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






