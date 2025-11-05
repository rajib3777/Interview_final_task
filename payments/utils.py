import hmac
import hashlib
from django.conf import settings

def verify_signature(raw_body: bytes, signature_from_header: str) -> bool:

    
    secret = getattr(settings, 'PAYMENT_WEBHOOK_SECRET', None)

    if not secret:
        
        return False
    

    computed = hmac.new(

        key=secret.encode('utf-8'),

        msg=raw_body,

        digestmod=hashlib.sha256

    ).hexdigest()

    

    return hmac.compare_digest(computed, (signature_from_header or ''))
