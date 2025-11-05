from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Payment
from .serializers import PaymentCreateSerializer, PaymentStatusSerializer
from .utils import verify_signature
import json


class PaymentCreateView(generics.CreateAPIView):

    serializer_class = PaymentCreateSerializer

    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data, context={'request': request})

        serializer.is_valid(raise_exception=True)

        payment = serializer.save()


        mock_checkout_url = f"https://sandbox.example-pay.local/checkout/{payment.transaction_id}"

        data = PaymentStatusSerializer(payment).data

        data.update({

            "message": "Payment initiated. Use the checkout_url to complete payment (mock).",
            "checkout_url": mock_checkout_url

        })

        return Response(data, status=status.HTTP_201_CREATED)


class PaymentWebhookView(APIView):

    permission_classes = [permissions.AllowAny] 

    def post(self, request, *args, **kwargs):

        
        raw = request.body

        signature = request.headers.get('X-Signature')

        if not verify_signature(raw, signature):

            return Response({"detail": "Invalid signature."}, status=status.HTTP_401_UNAUTHORIZED)

        try:

            payload = json.loads(raw.decode('utf-8'))

        except Exception:

            return Response({"detail": "Invalid JSON."}, status=status.HTTP_400_BAD_REQUEST)

        
        txid = payload.get('transaction_id')

        gw_ref = payload.get('gateway_reference')
        
        new_status = (payload.get('status') or '').upper()

        if not txid or new_status not in ['SUCCESS', 'FAILED', 'CANCELED']:

            return Response({"detail": "Missing or invalid fields."}, status=status.HTTP_400_BAD_REQUEST)

        payment = get_object_or_404(Payment, transaction_id=txid)

        
        if payment.status in ['SUCCESS', 'FAILED', 'CANCELED']:

           
            return Response({"detail": "Already finalized."}, status=status.HTTP_200_OK)

        payment.status = new_status

        payment.gateway_reference = gw_ref

        
        meta = payment.metadata or {}

        meta['webhook_payload'] = payload
        
        payment.metadata = meta

        payment.save(update_fields=['status', 'gateway_reference', 'metadata', 'updated_at'])
        

        return Response({"detail": "Payment updated.", "status": payment.status}, status=status.HTTP_200_OK)



class PaymentStatusView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
       
        txid = request.query_params.get('transaction_id')

        pid = request.query_params.get('id')


        if not txid and not pid:

            return Response({"detail": "Provide transaction_id or id."}, status=status.HTTP_400_BAD_REQUEST)
        

        qs = Payment.objects.all()

        if not (request.user.is_superuser or getattr(request.user, 'user_type', '') == 'ADMIN'):

            qs = qs.filter(user=request.user)


        if txid:

            payment = get_object_or_404(qs, transaction_id=txid)

        else:

            payment = get_object_or_404(qs, id=pid)



        data = PaymentStatusSerializer(payment).data

        
        return Response(data, status=status.HTTP_200_OK)

