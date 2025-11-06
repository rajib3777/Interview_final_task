import os, hmac, hashlib, requests, base64
from django.conf import settings

DEFAULT_TIMEOUT = 15  # seconds

def verify_signature(raw_body: bytes, signature_from_header: str) -> bool:
    """
    Verify webhook HMAC signature. If no signature and DEBUG=True, allow (sandbox/dev).
    """
    secret = getattr(settings, 'PAYMENT_WEBHOOK_SECRET', None)
    if not secret:
        # If no secret configured, allow only in DEBUG for sandbox convenience
        return bool(getattr(settings, 'DEBUG', False))
    if not signature_from_header:
        return bool(getattr(settings, 'DEBUG', False))
    computed = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, signature_from_header or '')

def get_bkash_token():
    """
    Fetch sandbox token from bKash Tokenized Checkout.
    bKash expects username/password in headers and app_key/app_secret in JSON body.
    """
    url = f"{settings.BKASH_BASE_URL}/tokenized/checkout/token/grant"
    payload = {
        "app_key": settings.BKASH_APP_KEY,
        "app_secret": settings.BKASH_APP_SECRET
    }
    headers = {
        "Content-Type": "application/json",
        "username": settings.BKASH_USERNAME,
        "password": settings.BKASH_PASSWORD,
    }
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=DEFAULT_TIMEOUT)
        print("🔹 BKASH TOKEN RESPONSE:", res.text)
        data = res.json() if res.headers.get("Content-Type","").startswith("application/json") else {}
        # success: {"id_token": "...", "token_type": "..." , "expires_in": ...}
        if res.status_code == 200 and data.get('id_token'):
            return data.get("id_token")
    except Exception as e:
        print("⚠️ bKash Token Error:", e)
    return None

def nagad_initiate_payment(amount, invoice_id):
    """Simulate Nagad sandbox checkout"""
    base_url = getattr(settings, 'NAGAD_BASE_URL', 'https://sandbox.mynagad.com')
    merchant_id = getattr(settings, 'NAGAD_MERCHANT_ID', getattr(settings, 'NAGAD_APP_MERCHANTID', '6800000025'))
    callback_url = f"{settings.SITE_URL}/api/payments/webhook/"

    payload = {
        "merchantId": merchant_id,
        "orderId": invoice_id,
        "currencyCode": "050",
        "amount": str(amount),
        "challenge": base64.b64encode(os.urandom(16)).decode(),
        "callbackUrl": callback_url,
        "productDetails": "Demo purchase"
    }

    headers = {"Content-Type": "application/json"}
    try:
        res = requests.post(
            f"{base_url}/remote-payment-gateway-1.0/api/dfs/check-out/initialize",
            json=payload,
            headers=headers,
            timeout=DEFAULT_TIMEOUT
        )
        print("🔹 NAGAD RESPONSE:", res.text)
        return res.json()
    except Exception as e:
        print("⚠️ Nagad Sandbox Error:", e)
        return {"error": "Nagad sandbox not reachable"}
