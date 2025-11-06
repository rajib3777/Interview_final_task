from rest_framework import serializers
from .models import Payment
import uuid


class PaymentCreateSerializer(serializers.ModelSerializer):
    payment_method = serializers.ChoiceField(choices=Payment.METHOD_CHOICES)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Payment
        fields = ['payment_method', 'amount']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        payment = Payment.objects.create(
            user=user,
            payment_method=validated_data['payment_method'],
            amount=validated_data['amount'],
            status='PENDING',
            transaction_id=str(uuid.uuid4()).replace('-', '')[:20],
        )
        return payment


class PaymentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
