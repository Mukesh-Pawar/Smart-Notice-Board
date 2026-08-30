# GSM-Based Smart Notice Board with Web-Based Department Notice Management System

A responsive Django + Django REST Framework application for managing department notices and exposing the current notice to an embedded GSM/LED notice-board controller.

## 1. Project Description

The system provides a secure web dashboard for HOD/Super Admins and approved Department Admins. New administrator registrations enter a **PENDING** state and cannot access the dashboard until an HOD approves them. Notices support priority, scheduling, duration-based expiry, history, cancellation, redisplay and a secure API for future embedded hardware integration.

## 2. Features

- Custom email-based Django user model
- HOD / Super Admin and Department Admin roles
- Pending → Approved / Rejected admin workflow
- Enable / disable approved admins
- Secure password hashing and validation
- Session-based web authentication
- Django password-reset flow with configurable email backend
- Responsive Bootstrap 5 UI
- Notice priority: Normal, Important, Emergency
- Notice lifecycle: Draft, Scheduled, Active, Expired, Cancelled
- Duration presets: 1h, 6h, 12h, 24h, 2d, 7d, Custom
- Server-side expiry calculation
- Current notice selection for the physical board
- Search, priority/status/date filtering and pagination
- Notice activity log
- Django admin configuration
- DRF token-authenticated API
- Hardware-independent GSM service abstraction
- Automated tests for core authentication, authorization, notice and API flows
- Environment-based secrets and deployment settings
- Friendly 400/403/404/500 error pages

## 3. Technology Stack

- Python 3
- Django 5.2
- Django REST Framework 3.16
- SQLite by default
- Bootstrap 5
- HTML5 / CSS3 / JavaScript
- Fetch API can be used by future hardware/admin clients
- Token Authentication for embedded/API clients
- `python-dotenv` for environment configuration

## 4. Architecture

```text
Browser (HOD/Admin)
        |
        v
Bootstrap + HTML/CSS/JS
        |
        v
Django Views / Forms
        |
        +---- Accounts + RBAC
        |
        +---- Notice Business Services
        |         |
        |         +---- Notice / NoticeLog
        |         |
        |         +---- GSM Service Abstraction
        |
        v
SQLite (local) / PostgreSQL or MySQL (future)

Embedded path:

Web Application
      |
      v
Django REST API
      |
      v
GSM / SMS Communication Layer
      |
      v
SIM800L / SIM900 / compatible modem
      |
      v
Microcontroller
      |
      v
P10 LED Display
```

Business logic for notice scheduling is kept in `notices/services.py`. GSM logic is isolated in `services/gsm_service.py`, so a serial modem adapter can be added without putting hardware code in Django views.

## 5. Folder Structure

```text
smart_notice_board/
├── manage.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── accounts/
│   ├── migrations/0001_initial.py
│   ├── management/commands/create_hod.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── permissions.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
├── notices/
│   ├── migrations/0001_initial.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── services.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
├── api/
│   ├── apps.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
├── services/
│   ├── __init__.py
│   └── gsm_service.py
├── templates/
│   ├── base.html
│   ├── registration/
│   ├── dashboard/
│   ├── hod/
│   ├── notices/
│   └── errors/
├── static/
│   ├── css/style.css
│   ├── js/app.js
│   └── images/
└── tests/
    └── __init__.py
```

## 6. Installation

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and change `SECRET_KEY` before using the application beyond a local demo.

```text
SECRET_KEY=your-long-random-secret
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

## 7. Database Setup

SQLite is used automatically.

```bash
python manage.py makemigrations
python manage.py migrate
```

The repository already includes initial migrations, so a clean clone can normally use `migrate` directly.

## 8. HOD / Super Admin Setup

Recommended project-specific setup:

```bash
python manage.py create_hod --email hod@example.com --name "Department HOD" --department "E&TC"
```

The command prompts for the password securely when `--password` is not supplied.

You can also use Django's standard command:

```bash
python manage.py createsuperuser
```

The custom user manager automatically assigns a superuser the HOD role and active status.

No HOD password is hard-coded in source code.

## 9. Run Development Server

```bash
python manage.py runserver
```

Open the displayed local server address in a browser.

Important pages:

- `/login/` — login
- `/register/` — Department Admin registration
- `/dashboard/` — role-specific dashboard
- `/notices/` — notice history
- `/notices/current-notice/` — current board notice
- `/admin/` — Django admin

## 10. Authentication Flow

```text
Registration
     |
     v
PENDING
     |
     +---- HOD Rejects ----> REJECTED (cannot login)
     |
     +---- HOD Approves ---> ACTIVE
                                |
                                v
                              LOGIN
                                |
                                v
                         Admin Dashboard
```

HOD can later disable an active admin. Disabled accounts cannot authenticate successfully.

## 11. Notice Lifecycle

```text
Create Notice
     |
     +---- Start time in future ----> SCHEDULED
     |
     +---- Start time now ----------> ACTIVE
                                        |
                                        v
                                    EXPIRED

Any active/scheduled notice may also be CANCELLED by an authorized user.
```

The backend calculates expiry using:

```text
expiry_time = start_time + duration_minutes
```

The frontend never gets authority to override the calculated expiry time.

## 12. REST API

All protected API endpoints use DRF Token Authentication or an authenticated Django session.

### Obtain API token

```http
POST /api/auth/login/
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "your-password"
}
```

Response includes a token for an active user.

Send it to protected endpoints:

```http
Authorization: Token YOUR_TOKEN
```

### Current notice

```http
GET /api/notices/current/
```

Response shape:

```json
{
  "success": true,
  "notice": {
    "id": 12,
    "title": "Practical Examination",
    "message": "E&TC practical examination will be conducted tomorrow at 10 AM.",
    "priority": "IMPORTANT",
    "start_time": "2026-08-19T09:00:00+05:30",
    "expiry_time": "2026-08-20T09:00:00+05:30",
    "status": "ACTIVE"
  }
}
```

The current-notice endpoint intentionally exposes only the minimum board-facing notice fields.

### History

```http
GET /api/notices/history/
GET /api/notices/history/?priority=IMPORTANT&status=EXPIRED
```

### Detail

```http
GET /api/notices/<id>/
```

### Create

```http
POST /api/notices/create/
Content-Type: application/json
Authorization: Token YOUR_TOKEN
```

Example body:

```json
{
  "title": "Practical Examination",
  "message": "Practical examination will be conducted tomorrow at 10 AM.",
  "priority": "IMPORTANT",
  "start_time": "2026-08-19T09:00:00+05:30",
  "duration": "24h"
}
```

Custom duration uses:

```json
{
  "duration": "custom",
  "custom_duration_minutes": 90
}
```

### Update

```http
PUT /api/notices/<id>/update/
```

### Delete / cancel

```http
DELETE /api/notices/<id>/delete/
```

For history integrity, this API operation cancels the notice rather than silently destroying its lifecycle record.

## 13. GSM Integration

The integration boundary is:

`services/gsm_service.py`

Available functions include:

- `format_notice_for_sms(notice)`
- `send_sms(phone_number, message)`
- `send_notice_via_gsm(notice)`

By default GSM is disabled. The service logs a simulated transmission instead of accessing hardware.

Future SIM800L/SIM900 integration can implement serial communication inside this service boundary. The Django views and notice models should not need to know modem-specific commands.

Example future environment configuration:

```text
GSM_ENABLED=True
GSM_SERIAL_PORT=COM5
GSM_BAUD_RATE=9600
GSM_SIM_NUMBER=your-target-number
```

Do not commit real phone numbers, credentials or modem secrets if they are confidential.

## 14. Password Reset / Email

For local development, `.env.example` uses:

```text
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

The reset URL and email contents will be printed in the terminal.

For real SMTP, configure:

```text
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=no-reply@example.com
```

Keep these values in `.env`, not in Git.

## 15. Security Practices

- Passwords use Django's secure password hashing.
- CSRF middleware protects web forms.
- Authorization checks enforce HOD/Admin roles.
- Pending/rejected/disabled accounts cannot access dashboards.
- DRF protected endpoints require authentication.
- Current-board API returns no user details.
- ORM queries are used instead of concatenated SQL.
- Django templates escape normal variable output by default.
- Secret key, email credentials and deployment settings are environment-based.
- Secure cookie/HSTS settings are enabled when `DEBUG=False`.
- Production `DEBUG` should always be `False`.
- `ALLOWED_HOSTS` is configurable.

## 16. Testing

Run all tests:

```bash
python manage.py test
```

Test coverage includes:

- Registration creates a pending account
- Pending login is rejected
- Approved login works
- Invalid credentials are rejected
- HOD approval flow
- Notice expiry calculation
- Current notice selection
- Expiry status transition
- Notice creation/update
- API authentication
- Current notice API
- Unauthorized API access
- Pending API login rejection

## 17. Git / GitHub Workflow

```bash
git init
git add .
git commit -m "Initial smart notice board project"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

Before pushing, verify:

```bash
git status
```

`.env`, `db.sqlite3`, virtual environments, caches and secrets are excluded by `.gitignore`.

## 18. MySQL / PostgreSQL Migration

The application uses SQLite for zero-configuration development. For production, configure Django's `DATABASES['default']` with PostgreSQL or MySQL and keep credentials in environment variables.

A common production direction is PostgreSQL + Gunicorn + Nginx, with HTTPS and a managed database.

## 19. Future Improvements

- Real SIM800L/SIM900 serial adapter
- P10 LED display protocol/driver
- Hardware heartbeat and device registration
- Notice acknowledgement / delivery status
- Scheduled background jobs with Celery or Django-Q
- Audit-log export
- HOD dashboard analytics
- Multi-department support with department-specific permissions
- PostgreSQL production database
- Redis caching for high-frequency board polling
- Device API keys with rotation and expiry
- Rate limiting and API throttling
- Docker deployment

## 20. Suggested Team Member Task Division

| Member | Responsibility |
|---|---|
| Member 1 | Django backend, models, authentication and RBAC |
| Member 2 | Frontend, Bootstrap UI, responsive design |
| Member 3 | REST API, testing and security |
| Member 4 | GSM/microcontroller/P10 hardware integration |
| Member 5 | Documentation, deployment, testing and final presentation |

For a smaller team, combine backend + API and frontend + documentation responsibilities.

## 21. Engineering Project Demonstration Flow

1. Create HOD using `create_hod`.
2. Start the server.
3. Register a new Department Admin.
4. Show that the new account is pending and cannot log in.
5. Log in as HOD.
6. Approve the registration request.
7. Log in as the approved Admin.
8. Create an Important notice with a short duration.
9. Open Current Notice and demonstrate the board-facing view.
10. Call `/api/notices/current/` using a token.
11. Show notice history and expiry state.
12. Disable the admin from the HOD panel.
13. Explain how `services/gsm_service.py` becomes the hardware integration boundary.

