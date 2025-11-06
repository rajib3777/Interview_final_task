from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Payment
from .serializers import PaymentCreateSerializer, PaymentStatusSerializer
from .utils import get_bkash_token, nagad_initiate_payment, verify_signature
from django.conf import settings
import requests, uuid, json

DEFAULT_TIMEOUT = 20  

class PaymentCreateView(generics.CreateAPIView):
    
    serializer_class = PaymentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()

        
        if payment.payment_method == 'BKASH':
            
            token = get_bkash_token()
            if not token:
                return Response(
                    {"detail": "Unable to obtain bKash sandbox token. Check BKASH_* credentials."},
                    status=status.HTTP_502_BAD_GATEWAY
                )

            headers = {
                "Authorization": f"Bearer {token}",
                "X-APP-Key": settings.BKASH_APP_KEY,
                "Content-Type": "application/json"
            }

            payload = {
                
                "mode": "0011",
                "payerReference": str(request.user.id),
                "callbackURL": f"{settings.SITE_URL}/api/payments/webhook/",
                "amount": str(payment.amount),
                "currency": "BDT",
                "intent": "sale",
                "merchantInvoiceNumber": str(uuid.uuid4())[:10],
            }

            url = f"{settings.BKASH_BASE_URL}/tokenized/checkout/create"
            
            try:
                res = requests.post(url, json=payload, headers=headers, timeout=DEFAULT_TIMEOUT)
                
            except Exception as e:
                return Response(
                    {"detail": f"bKash create error: {e}"},
                    status=status.HTTP_502_BAD_GATEWAY
                )

            try:
                data = res.json()
                # Typical success fields: paymentID, bkashURL
                payment.gateway_reference = data.get("paymentID") or payment.gateway_reference
                payment.status = 'PROCESSING'
                payment.save(update_fields=["gateway_reference", "status"])
                
            except Exception:
                data = {"error": "Invalid response from bKash sandbox."}

           
            out = {
                "transaction_id": payment.transaction_id,
                "status": payment.status,
                "gateway_response": data
            }
            
            return Response(out, status=res.status_code)

       
        elif payment.payment_method == 'NAGAD':
            
            resp = nagad_initiate_payment(payment.amount, str(uuid.uuid4())[:10])
            payment.status = 'PROCESSING'
            payment.save(update_fields=["status"])
            
            return Response(
                {"transaction_id": payment.transaction_id, "status": payment.status, "gateway_response": resp},
                status=status.HTTP_201_CREATED
            )

        return Response({"error": "Unsupported payment method."}, status=status.HTTP_400_BAD_REQUEST)


class PaymentWebhookView(APIView):
    
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        
        raw = request.body or b""
        signature = request.headers.get('X-Signature')

        
        
        if not verify_signature(raw, signature) and not getattr(settings, "DEBUG", False):
            return Response({"detail": "Invalid signature."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            payload = json.loads(raw.decode('utf-8') or "{}")
            
        except Exception:
            return Response({"detail": "Invalid JSON."}, status=status.HTTP_400_BAD_REQUEST)

        
        txid = payload.get('transaction_id')
        gateway_ref = payload.get('paymentID') or payload.get('gateway_reference')
        new_status = (payload.get('status') or '').upper()

        payment = None
        
        if txid:
            payment = get_object_or_404(Payment, transaction_id=txid)
        elif gateway_ref:
            payment = get_object_or_404(Payment, gateway_reference=gateway_ref)
        else:
            return Response({"detail": "Missing transaction identifiers."}, status=status.HTTP_400_BAD_REQUEST)

        if new_status in ['SUCCESS', 'FAILED', 'CANCELED']:
            
            payment.status = new_status
            payment.metadata['webhook_payload'] = payload
            payment.save(update_fields=['status', 'metadata'])

        return Response({"status": payment.status, "transaction_id": payment.transaction_id}, status=status.HTTP_200_OK)


class PaymentStatusView(APIView):
    
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        
        txid = request.query_params.get('transaction_id')
        payment = get_object_or_404(Payment, transaction_id=txid, user=request.user)
        return Response(PaymentStatusSerializer(payment).data, status=status.HTTP_200_OK)
