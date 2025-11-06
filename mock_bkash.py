from flask import Flask, request, jsonify
import uuid, time

app = Flask(__name__)

# Simple in-memory store to hold created payments
PAYMENTS = {}

@app.route("/v1.2.0-beta/tokenized/checkout/token/grant", methods=["POST"])
def token_grant():
    # Expect headers username/password; body app_key/app_secret
    username = request.headers.get("username")
    password = request.headers.get("password")
    body = request.get_json(silent=True) or {}
    app_key = body.get("app_key")
    app_secret = body.get("app_secret")

    # Very permissive: if present, return fake token
    if username and password and app_key and app_secret:
        token = "MOCK_BKASH_TOKEN_" + uuid.uuid4().hex
        resp = {"id_token": token, "token_type": "Bearer", "expires_in": "3600"}
        return jsonify(resp), 200

    return jsonify({"message": "Missing required request parameters: [password, username]"}), 400


@app.route("/v1.2.0-beta/tokenized/checkout/create", methods=["POST"])
def create_payment():
    auth = request.headers.get("Authorization", "")
    xapp = request.headers.get("X-APP-Key")
    if not auth.startswith("Bearer "):
        return jsonify({"message": "Unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    amount = payload.get("amount")
    merchantInvoiceNumber = payload.get("merchantInvoiceNumber") or str(uuid.uuid4())[:10]
    payment_id = "MOCKPAY" + uuid.uuid4().hex[:16]

    # store simulated payment
    PAYMENTS[payment_id] = {
        "paymentID": payment_id,
        "status": "INITIATED",
        "amount": amount,
        "merchantInvoiceNumber": merchantInvoiceNumber,
        "created_at": int(time.time())
    }

    # typical bKash response contains paymentID and a redirect url (bkashURL)
    return jsonify({
        "paymentID": payment_id,
        "bkashURL": f"https://mock.bkash.local/checkout/{payment_id}",
        "status": "SUCCESS"
    }), 200


@app.route("/v1.2.0-beta/tokenized/checkout/execute/<payment_id>", methods=["POST"])
def execute(payment_id):
    # simulate the user completed the payment at bKash side
    if payment_id not in PAYMENTS:
        return jsonify({"message": "Not found"}), 404
    PAYMENTS[payment_id]["status"] = "SUCCESS"
    return jsonify({"paymentID": payment_id, "status": "SUCCESS"}), 200


# Simulate webhook sender (for developer convenience)
@app.route("/v1.2.0-beta/mock/send_webhook/<payment_id>", methods=["POST"])
def send_webhook(payment_id):
    # This endpoint doesn't exist on real bKash; it's for local dev only.
    # It will POST to your app's webhook endpoint (SITE_URL/api/payments/webhook/)
    import requests, json
    if payment_id not in PAYMENTS:
        return jsonify({"message": "Not found"}), 404

    site = request.args.get("site", "http://127.0.0.1:8000")
    webhook_url = f"{site}/api/payments/webhook/"
    payload = {
        "paymentID": payment_id,
        "status": "SUCCESS",
        "transaction_id": request.args.get("txid") or ""
    }
    try:
        r = requests.post(webhook_url, json=payload, timeout=5)
        return jsonify({"posted_to": webhook_url, "status_code": r.status_code, "response_text": r.text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("Mock bKash server running at http://127.0.0.1:9000")
    app.run(port=9000)
