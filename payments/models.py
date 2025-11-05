from django.db import models
from django.conf import settings
import uuid

class Payment(models.Model):

    METHOD_CHOICES = (
        
        ('BKASH', 'Bkash'),
        ('NAGAD', 'Nagad'),

    )


    STATUS_CHOICES = (

        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('CANCELED', 'Canceled'),

    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')


    payment_method = models.CharField(max_length=10, choices=METHOD_CHOICES)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    currency = models.CharField(max_length=8, default='BDT')


    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='PENDING')


    
    transaction_id = models.CharField(max_length=64, unique=True)


    gateway_reference = models.CharField(max_length=128, blank=True, null=True, db_index=True)

  
    idempotency_key = models.CharField(max_length=64, blank=True, null=True, unique=True)

    
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:

        ordering = ['-created_at']


    def __str__(self):

        return f'{self.payment_method} {self.amount} {self.currency} [{self.status}] - {self.transaction_id}'
