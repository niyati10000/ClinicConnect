# 🏥 ClinicConnect — Multi-Tenant Healthcare & Clinic Management 

**Hostedlink**
https://niyati26.pythonanywhere.com/

**ClinicConnect** is an enterprise-grade, multi-tenant Clinic Operations and Electronic Health Record (EHR) platform. It is engineered specifically for hospitals, polyclinics, and rural healthcare centers with **offline-first SMS sync capabilities**, **conflict-free scheduling**, **pharmacy inventory tracking**, and **strict tenant data isolation**.

---

## 🌟 1. What Problem Does It Solve?
Most healthcare software is either too complicated, lacks offline capabilities for areas with unstable internet, or fails to strictly partition data when multiple organizations use the same system.

ClinicConnect solves this by providing:
1. **Multi-Tenancy for Organizations:** Multiple independent clinics can sign up and use the platform with complete, airtight data isolation.
2. **Offline-Resilient Workflow:** Receptionists can book appointments and prescribe medications even without internet; the system queues notifications and auto-syncs them via SMS once back online.
3. **Zero Conflict Scheduling:** A dynamic 30-minute booking engine prevents doctor double-booking.
4. **Automated Clinical Pharmacy & Billing:** Writing a prescription automatically checks stock, deducts inventory, and generates an itemized invoice.

---

## 🚀 2. Key Features & Modules

### 🏢 A. Multi-Tenant SaaS Architecture
* **Self-Serve Clinic Registration (`/auth/register`):** Different clinic organizations can create their own accounts with unique License Codes.
* **Airtight Tenant Data Isolation:** All database queries are cryptographically bound to the authenticated `clinic_id` (zero IDOR vulnerabilities).

### 👥 B. Role-Based Dual Workspaces
* **Receptionist View:** Patient check-in, dynamic slot booking, payment collection, and medicine inventory restocking.
* **Doctor Consultation Room:** Digital EHR consultation console, vitals logging (BP, Pulse, Temperature, SPO2), and instant prescription generator.

### 📅 C. Smart Scheduling Engine
* Divides doctor shifts into automatic 30-minute consultation slots.
* Real-time collision validation prevents duplicate appointments for the same doctor at the same time.

### 💊 D. Integrated Pharmacy & Auto-Billing
* **Live Stock Tracking:** Real-time stock counts with color-coded Low Stock warnings.
* **Prescription Auto-Deduction:** Prescribing medicines automatically decreases pharmacy stock levels.
* **Automated Invoicing:** Combines the doctor's consultation fee with the prescribed medicine costs into a printable, itemized invoice.

### 📶 E. Offline-First SMS Sync Hub
* Includes a real-time **Network Status Toggle** (`Online` / `Offline`).
* In offline mode, patient appointment confirmations are held in an asynchronous **Sync Queue (`Pending`)**.
* Switching back online allows a 1-click sync to dispatch SMS notifications via the **Twilio SMS Gateway**.

### 🌐 F. Accessibility & Modern UI
* **Bilingual Translation Switcher:** Full 1-click toggle between **English** and **Hindi (हिन्दी)**.
* **Dual Theme Engine:** Sleek Dark Mode and clean Light Mode.
* **Responsive Bento Grid:** Designed for widescreen reception monitors, laptops, and tablets.

---

## 🛡️ 3. Built-In Security Architecture

```
[ Client Request ]
       │
       ▼
[ Security Headers & CSP ]  ──► (Mitigates XSS & Clickjacking)
       │
       ▼
[ Active CSRF Token Middleware ] ──► (Blocks forged POST/PUT/DELETE requests)
       │
       ▼
[ Brute-Force Rate Limiter ] ──► (5-min lockout after 5 failed login attempts)
       │
       ▼
[ Tenant Boundary Enforcement ] ──► (WHERE clinic_id = session['clinic_id'])
       │
       ▼
[ SQLAlchemy Parameterized Queries ] ──► (Zero SQL Injection)
```

* **Salted PBKDF2 Password Hashing:** Passwords are never stored in plaintext (`werkzeug.security`).
* **Session Fixation Defense:** Clears and regenerates session tokens upon login and role switching.
* **OWASP Cookie Directives:** `HttpOnly=True`, `SameSite='Lax'`, and 2-hour inactivity lifetime.
* **Error Masking:** Custom 403, 404, and 500 error pages suppress database schema leaks and stack traces.

---

## 🛠️ 4. Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Backend Framework** | Python 3.10+, Flask 2.3+ (Modular Blueprints Architecture) |
| **Database & ORM** | Flask-SQLAlchemy (SQLAlchemy 2.0), SQLite (Local) / PostgreSQL (Cloud) |
| **Database Adapter** | `psycopg2-binary` (for zero-config PostgreSQL switching) |
| **WSGI Production Servers** | Gunicorn (Linux/Docker/Cloud), Waitress (Windows) |
| **Frontend** | Semantic HTML5, Vanilla CSS3 (Custom Design System, Bento Grid), Vanilla JS |
| **Typography & Icons** | Outfit & Plus Jakarta Sans (Google Fonts), FontAwesome 6 |
| **External APIs** | Twilio SMS API |
| **Test Suite** | Pytest (7/7 Automated Integration Tests) |

---

## 📂 5. Project Directory Structure

```text
clinic_connect/
├── app.py                     # Local development entrypoint
├── wsgi.py                    # Production WSGI application entrypoint
├── requirements.txt           # Python dependencies
├── Procfile                   # Cloud PaaS deployment file (Render/Railway/Heroku)
├── Dockerfile                 # Multi-stage container deployment
├── docker-compose.yml         # Containerized Flask + PostgreSQL setup
├── render.yaml                # 1-Click Render Cloud Infrastructure blueprint
├── tests/
│   └── test_clinic_connect.py # 7 automated unit & integration tests
└── clinic_connect/
    ├── __init__.py            # Application factory, CSRF & Security middleware
    ├── config.py              # Environment configuration & DB path normalizer
    ├── database.py            # SQLAlchemy database instance
    ├── models/                # 9 Relational database models
    │   ├── clinic.py          # Tenant organization accounts
    │   ├── patient.py         # Patient demographic records
    │   ├── doctor.py          # Doctor profiles & shift hours
    │   ├── appointment.py     # Slot scheduling model
    │   ├── prescription.py    # Digital EHR prescriptions
    │   ├── inventory.py       # Pharmacy stock management
    │   ├── invoice.py         # Billing & payment tracking
    │   ├── sync_log.py        # Offline SMS queue
    │   └── audit_log.py       # Compliance & action logs
    ├── routes/                # Blueprint controller routes
    │   ├── auth.py            # Login, registration & rate limiter
    │   ├── dashboard.py       # Role analytics & metrics API
    │   ├── patients.py        # Patient registration & timeline
    │   ├── doctors.py         # Consultation console & vitals
    │   ├── appointments.py    # 30-min slot booking engine
    │   ├── billing.py         # Invoices & payment recorder
    │   ├── inventory.py       # Stock adjustments
    │   └── sync.py            # SMS sync dispatcher
    ├── static/                # Styles & client scripts
    │   ├── css/style.css      # Design system & Bento grid styles
    │   └── js/main.js         # Theme & language switcher
    └── templates/             # Jinja2 template views
```

---

## ⚡ 6. How to Run Locally

### Prerequisites
* Python 3.10+ installed

### Setup Commands
```bash
# 1. Clone the repository
git clone https://github.com/niyati10000/ClinicConnect.git
cd ClinicConnect

# 2. Create and activate a virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run automated tests
python -m pytest

# 5. Start the application
python app.py
```
Open **`http://127.0.0.1:5000`** in your browser!
