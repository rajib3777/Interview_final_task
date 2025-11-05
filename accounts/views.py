from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404, render
from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer



class RegisterView(generics.CreateAPIView):
    
    queryset = User.objects.all()
    
    serializer_class = RegisterSerializer
    
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data, context={'request': request})
        
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        
        return Response({
            "message": "Registration successful! Please verify your email.",
            
            "user": UserSerializer(user["user"]).data,
            
            "token": user["token"],
            
            "activation_link": user["activation_link"]
            
        }, status=status.HTTP_201_CREATED)
        
        
class LoginView(APIView):
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        
        serializer = LoginSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            
            "message": "Login successful.",
            
            "token": token.key,
            
            "user": {
                
                "id": user.id,
                
                "email": user.email,
                
                "username": user.username,
                
                "full_name": user.full_name,
                
                "user_type": user.user_type,
            }   
            
        }, status=status.HTTP_200_OK)
        
    

class LogoutView(APIView):
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        
        request.user.auth_token.delete()
        
        logout(request)
        
        return Response(
            {"message": "Logged out successfully."},
            
            status=status.HTTP_200_OK
        )   
        


class ProfileView(generics.RetrieveUpdateAPIView):
    
    serializer_class = UserSerializer
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        
        return self.request.user
    
    
    def retrieve(self, request, *args, **kwargs):
        
        user = self.get_object()
        
        serializer = self.get_serializer(user)

        return Response({
            
            "profile": serializer.data
            
        }, status=status.HTTP_200_OK)
        
        
    def update(self, request, *args, **kwargs):
        
        user = self.get_object()
        
        serializer = self.get_serializer(user, data=request.data, partial=True)
        
        serializer.is_valid(raise_exception=True)
        
        serializer.save()
        
        return Response({
            
            "message": "Profile updated successfully.",
            
            "profile": serializer.data
            
        }, status=status.HTTP_200_OK)
        
        

class ActivateAccountView(APIView):

    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token):

        try:
            uid = urlsafe_base64_decode(uidb64).decode()

            user = get_object_or_404(User, pk=uid)

        except Exception:

            return render(request, 'accounts/activation_failed.html')
        

        if default_token_generator.check_token(user, token):

            user.is_active = True

            user.save()

            return render(request, 'accounts/activation_success.html')
        
        else:

            return render(request, 'accounts/activation_failed.html')
