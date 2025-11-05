from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models



#custom call
class UserManager(BaseUserManager):
    
    def create_user(self, email, full_name=None, password=None, **extra_fields):
        
        if not email:
            raise ValueError("Email address is required")
        
        email = self.normalize_email(email)
        
        user = self.model(email=email, full_name=full_name, **extra_fields)
        
        user.set_password(password)
        
        user.save(using=self._db)
        
        return user

    def create_superuser(self, email, full_name=None, password=None, **extra_fields):
        
        extra_fields.setdefault("is_staff", True)
        
        extra_fields.setdefault("is_superuser", True)
        
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            
            raise ValueError("Superuser must have is_staff=True.")
        
        if extra_fields.get("is_superuser") is not True:
            
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, full_name, password, **extra_fields)




def user_directory_path(instance, filename):
    
    return f'user_{instance.pk or "temp"}/{filename}'



class User(AbstractUser):

        ROLE_CHOICES = (
            ('ADMIN', 'Admin'),
            ('STAFF', 'Staff'),
            ('USER', 'User'),
        )
        
        user_type = models.CharField(max_length=10, choices=ROLE_CHOICES, default='USER')
        
        phone = models.CharField(max_length=20, blank=True, null=True)
        
        full_name = models.CharField(max_length=255, blank=True, null=True)
        
        address = models.CharField(max_length=255, blank=True, null=True)
        
        image = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
        
        email = models.EmailField(unique=True)

        is_active = models.BooleanField(default=False)
        
        
        objects = UserManager()
        
        
        username = models.CharField(max_length=150)
        
        USERNAME_FIELD = 'email'
        
        REQUIRED_FIELDS = ['username','full_name']
        
    

        def __str__(self):
            return f"{self.username} ({self.user_type})"
        

