from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    ActivateAccountView,
)

urlpatterns = [

    path('register/', RegisterView.as_view(), name='register'),
    
    path('login/', LoginView.as_view(), name='login'),

    path('logout/', LogoutView.as_view(), name='logout'),

    path('profile/', ProfileView.as_view(), name='profile'),

    
    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate'),
]
