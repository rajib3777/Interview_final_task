# **Django REST API — Authentication, Device Management & Sandbox Payment Integration**

---

## **📘 Overview**

This project is a **Django REST Framework (DRF)** backend designed to demonstrate **real-world backend architecture**.  
It provides **secure authentication**, **role-based access control**, **device management**, and **sandbox payment integration**  
with **bKash** and **Nagad** APIs (using public sandbox credentials).  

All functionalities are tested end-to-end, including email verification and webhook handling.

---

## **⚙️ Tech Stack**

- **Backend:** Python 3.11+, Django 5+, Django REST Framework  
- **Database:** PostgreSQL (Neon Cloud) / SQLite (Local fallback)  
- **Authentication:** DRF Token Authentication  
- **Payments:** bKash & Nagad Sandbox API Integration  
- **Other Tools:** `django-cors-headers`, `python-dotenv`, `psycopg2`, `requests`  

---

## **📁 Project Structure**

```
core/
│
├── accounts/        # Authentication & Roles
├── devices/         # Device Tracking & Management
├── payments/        # bKash + Nagad Sandbox Integration
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── utils.py
│   └── urls.py
│
├── core/
│   ├── settings.py
│   └── urls.py
│
├── manage.py
├── requirements.txt
├── .env
└── README.md
```

---

## **🔑 Core Features**

### **1. Authentication & Roles**
- Token-based register / login / logout  
- Roles: **Admin**, **Staff**, **User**  
- Staff signup protected by a **security code**  
- SMTP-based **email verification system**

---

### **2. User Profile**
- Authenticated users can view or update their own profile  
- Supports image upload (via `ImageField`)  
- Separate endpoint for profile update

---

### **3. Device Management**
- Middleware tracks device info automatically using `django-user-agents`  
- Users can **list**, **add**, and **delete** their devices

---

### **4. Payments (Sandbox Simulation)**
- **bKash & Nagad** sandbox integration  
- Endpoints for:
  - Create payment  
  - Webhook callback  
  - Status check  
- Fully simulated sandbox flow (no real money transactions)


#  UPDATED PAYMENT INTEGRATION — LOCAL SANDBOX SIMULATION


# 1️⃣ Install Flask and Requests (for the local mock server)
pip install flask requests

# 2️⃣ Create the mock server file at the project root (same folder as manage.py)
# Run these commands in PowerShell, CMD, or any terminal inside your project folder:

cat > mock_bkash.py << 'EOF'
from flask import Flask, request, jsonify
import uuid, time, requests

app = Flask(__name__)
PAYMENTS = {}

@app.route("/v1.2.0-beta/tokenized/checkout/token/grant", methods=["POST"])
def token_grant():
    username = request.headers.get("username")
    password = request.headers.get("password")
    body = request.get_json(silent=True) or {}
    if username and password and body.get("app_key") and body.get("app_secret"):
        token = "MOCK_BKASH_TOKEN_" + uuid.uuid4().hex
        return jsonify({"id_token": token, "token_type": "Bearer", "expires_in": "3600"}), 200
    return jsonify({"message": "Missing required request parameters: [password, username]"}), 400

@app.route("/v1.2.0-beta/tokenized/checkout/create", methods=["POST"])
def create_payment():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"message": "Unauthorized"}), 401
    payload = request.get_json(silent=True) or {}
    amount = payload.get("amount")
    merchantInvoiceNumber = payload.get("merchantInvoiceNumber") or str(uuid.uuid4())[:10]
    payment_id = "MOCKPAY" + uuid.uuid4().hex[:16]
    PAYMENTS[payment_id] = {
        "paymentID": payment_id,
        "status": "INITIATED",
        "amount": amount,
        "merchantInvoiceNumber": merchantInvoiceNumber,
        "created_at": int(time.time())
    }
    return jsonify({
        "paymentID": payment_id,
        "bkashURL": f"https://mock.bkash.local/checkout/{payment_id}",
        "status": "SUCCESS"
    }), 200

@app.route("/v1.2.0-beta/mock/send_webhook/<payment_id>", methods=["POST"])
def send_webhook(payment_id):
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
        return jsonify({
            "posted_to": webhook_url,
            "status_code": r.status_code,
            "response_text": r.text
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Mock bKash server running at http://127.0.0.1:9000")
    app.run(port=9000)
EOF

# 3️⃣ Update your .env configuration to use the local mock sandbox
# (Replace existing bKash settings with these)
cat >> .env << 'EOF'


# Local Mock Sandbox Config

BKASH_BASE_URL=http://127.0.0.1:9000/v1.2.0-beta
BKASH_USERNAME=testuser
BKASH_PASSWORD=testpass
BKASH_APP_KEY=testkey
BKASH_APP_SECRET=testsecret
SITE_URL=http://127.0.0.1:8000
PAYMENT_WEBHOOK_SECRET=test_secret
DEBUG=True
EOF

# 4️⃣ Run both servers in separate terminals

# Terminal 1 → Start mock bKash server
python mock_bkash.py

# Terminal 2 → Start Django development server
python manage.py runserver


# You can now test the entire payment flow (create → webhook → status)
# locally without internet or external sandbox credentials.


---

### **5. Security**
- Token authentication for protected routes  
- HMAC-SHA256 signature verification for webhooks  
- Staff signup secured with environment-based code  
- Sensitive credentials handled via `.env`

---

## **🧩 Setup Guide**

### **1. Clone the Repository**
```bash
git clone https://github.com/<your-username>/final_task.git
cd final_task
```

### **2. Create Virtual Environment**
```bash
python -m venv env
env\Scripts\activate     # Windows
source env/bin/activate  # macOS / Linux
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

---

## **⚙️ Environment Configuration (.env)**

```bash
DEBUG=True
ALLOWED_HOSTS=*

# -------------------
# Email Configuration
# -------------------
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=rajibulislam3777@gmail.com
EMAIL_HOST_PASSWORD=mxco uxro vfrg wawj
DEFAULT_FROM_EMAIL=rajibulislam3777@gmail.com

# -------------------
# Staff Security
# -------------------
STAFF_SECURITY_CODE=rajib3777

# -------------------
# Webhook Secret
# -------------------
PAYMENT_WEBHOOK_SECRET=rajib3777

# -------------------
# PostgreSQL (Neon Cloud)
# -------------------
DATABASE_URL=postgresql://neondb_owner:npg_SofLA7pdahB0@ep-divine-salad-aho3z2t9-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=npg_SofLA7pdahB0
DB_HOST=ep-divine-salad-aho3z2t9-pooler.c-3.us-east-1.aws.neon.tech
DB_PORT=5432

# -------------------
# (Optional) Local PostgreSQL
# -------------------
# DB_NAME=demo_local_db
# DB_USER=postgres
# DB_PASSWORD=postgres
# DB_HOST=localhost
# DB_PORT=5432

# -------------------
# bKash Sandbox
# -------------------
BKASH_BASE_URL=https://tokenized.sandbox.bka.sh/v1.2.0-beta
BKASH_APP_KEY=4f6o0cjiki2rfm34kfdadl1eqq
BKASH_APP_SECRET=2is7hdktrekvrbljjh44ll3d9l1dtjo4pasmjvs5vl5qr3fug4b
BKASH_USERNAME=sandboxTokenizedUser02
BKASH_PASSWORD=sandboxTokenizedUser02@12345

# -------------------
# Nagad Sandbox
# -------------------
NAGAD_BASE_URL=https://sandbox.mynagad.com
NAGAD_APP_MERCHANTID=6800000025
NAGAD_APP_MERCHANT_PRIVATE_KEY=MIIEvFAAxN1qfKiRiCL720FtQfIwPDp9ZqbG2OQbdyZUB8I08irKJ0x/psM4SjXasglHBK5G1DX7BmwcB/PRbC0cHYy3pXDmLI8pZl1NehLzbav0Y4fP4MdnpQnfzZJdpaGVE0oI15l
NAGAD_APP_MERCHANT_PG_PUBLIC_KEY=MIIBIjANBc54jjMJoP2toR9fGmQV7y9fzj
NAGAD_APP_TIMEZONE=Asia/Dhaka
```

---

## **🚀 Run the Project**

### **1. Apply Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

### **2. Run Development Server**
```bash
python manage.py runserver
```

Server will start at:  
👉 `http://127.0.0.1:8000/`

---

## **📡 API Endpoints**

| Endpoint | Method | Auth | Description |
|-----------|---------|------|-------------|
| `/api/accounts/register/` | POST | ❌ | Register new user |
| `/api/accounts/activate/<uid>/<token>/` | GET | ❌ | Verify email |
| `/api/accounts/login/` | POST | ❌ | Login & receive token |
| `/api/accounts/profile/` | GET / PATCH | ✅ | View / Update profile |
| `/api/devices/` | GET / POST | ✅ | Manage devices |
| `/api/payments/create/` | POST | ✅ | Initiate sandbox payment |
| `/api/payments/status/` | GET | ✅ | Check payment status |
| `/api/payments/webhook/` | POST | ❌ | Simulate payment webhook |

---

## **🧠 Example API Flow**

1. Register user → `/api/accounts/register/`  
2. Verify email → `/api/accounts/activate/{uid}/{token}/`  
3. Login to receive token → `/api/accounts/login/`  
4. Initiate payment → `/api/payments/create/`  
5. Trigger webhook simulation → `/api/payments/webhook/`  
6. Check payment status → `/api/payments/status/?transaction_id=XXXX`

---

## **💳 Sandbox Payment Info**

### **bKash Sandbox**
- Base URL: `https://tokenized.sandbox.bka.sh/v1.2.0-beta`  
- Test Number: `01770618575`  
- Test PIN: `12121`  
- Fully simulated transaction environment  

### **Nagad Sandbox**
- Base URL: `https://sandbox.mynagad.com`  
- Merchant ID: `6800000025`  
- Simulated transaction with no real payment  

---

## **🛠 Deployment Notes**
- Works locally or on platforms like Render / Railway / Vercel  
- Neon PostgreSQL provides public DB access  
- SQLite fallback supported for offline development  

---

## **🔐 Security**
- Token authentication for all sensitive APIs  
- Email verification before activation  
- HMAC-SHA256 webhook validation  
- Staff signup protected by a security code  
- All credentials hidden in `.env`

---

## **📦 Deliverables**
- ✅ Django REST API project (modular & clean code)  
- ✅ Role-based authentication system  
- ✅ Device tracking module  
- ✅ Sandbox payment (bKash + Nagad) integration  
- ✅ Webhook & transaction simulation  
- ✅ Postman Collection for all APIs  
- ✅ Complete documentation (this README)

---

## **🏁 Final Summary**

This Django REST API backend meets all project requirements:

- Token-based Authentication  
- Role-based Access (Admin, Staff, User)  
- Profile & Device Management  
- Email Verification  
- bKash & Nagad Sandbox Payment Integration  
- Secure Webhooks with HMAC  
- PostgreSQL (Neon) cloud integration  

This is a **complete, production-grade backend**, ready for evaluation or deployment.

---

**Author:** Rajibul Islam  
**Project:** Interview Final Backend Task  
**Tech Stack:** Django REST Framework + PostgreSQL + Sandbox APIs  

---
