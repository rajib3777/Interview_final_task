from rest_framework import serializers
from .models import Payment
import uuid
from django.conf import settings


class PaymentCreateSerializer(serializers.ModelSerializer):

    payment_method = serializers.ChoiceField(choices=Payment.METHOD_CHOICES)

    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    idempotency_key = serializers.CharField(required=False, allow_blank=True, allow_null=True)


    class Meta:

        model = Payment

        fields = ['payment_method', 'amount', 'idempotency_key']


    def validate_amount(self, value):

        if value <= 0:

            raise serializers.ValidationError("Amount must be greater than 0.")
        
        return value
    

    def create(self, validated_data):

        user = self.context['request'].user
        
        idem = validated_data.get('idempotency_key')

        if idem:

            existing = Payment.objects.filter(user=
            user, idempotency_key=idem).first()

            if existing:

                return existing
            

        payment = Payment.objects.create(

            user=user,

            payment_method=validated_data['payment_method'],

            amount=validated_data['amount'],

            status='PENDING',

            transaction_id=str(uuid.uuid4()).replace('-', '')[:24],

            idempotency_key=idem or None,

            metadata={

                "create_initiator": "api",
                "frontend_success_url": getattr(settings, 'PAYMENT_SUCCESS_URL', None),
                "frontend_failure_url": getattr(settings, 'PAYMENT_FAILURE_URL', None),

            }
        )

        return payment
    
    


class PaymentStatusSerializer(serializers.ModelSerializer):
        
    class Meta:
        
        model = Payment

        fields = [
             
            'id', 'transaction_id', 'payment_method', 'amount', 'currency',
            'status', 'gateway_reference', 'metadata', 'created_at', 'updated_at'

        ]
