from django.db import models
from django.conf import settings


class Device(models.Model):

    DEVICE_TYPES = (

        ('MOBILE', 'Mobile'),
        ('TABLET', 'Tablet'),
        ('LAPTOP', 'Laptop'),
        ('DESKTOP', 'Desktop'),
        ('OTHER', 'Other'),

    )

    user = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.CASCADE,

        related_name='devices'
    )

    device_name = models.CharField(max_length=100)

    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES, default='OTHER')

    os_version = models.CharField(max_length=50, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return f"{self.device_name} ({self.device_type}) - {self.user.email}"
    

    class Meta:
        
        ordering = ['-created_at']

