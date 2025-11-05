from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout
from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer



class RegisterView(generics.CreateAPIView):
    
    queryset = User.objects.all()
    
    serialzer_class = RegisterSerializer
    
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            
            "message": "Registration successful.",
            
            "user": {
                
                "id": user.id,
                
                "email": user.email,
                
                "username": user.username,
                
                "full_name": user.full_name,
                
                "user_type": user.user_type,
            },
            "token": token.key
            
        }, status=status.HTTP_201_CREATED)
        
    
class LoginView(APIView):
    
    permission_classes = [permissions.AllowAny]
    
    def post(Self, request):
        
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
    
    serializer = UserSerializer
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        
        return self.request.user
    
    
    def retrive(self, request, *args, **kwargs):
        
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
        
        

