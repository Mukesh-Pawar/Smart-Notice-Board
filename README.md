Smart Notice Board

Server-Based Smart Notice Board with REST API and IoT Display Integration

Smart Notice Board is a web-based department notice management system developed using Django. It provides a centralized platform where the Head of Department (HOD) and authorized Department Administrators can manage department notices, user accounts, profile information, and administrative requests.

The system uses a Django backend and REST API to provide notice information to a device controller. A virtual ESP32 simulator retrieves notice data from the API and displays it across two virtual P10 panels connected as one continuous display.

The software and virtual testing setup have been tested locally. Physical ESP32 and P10 hardware integration will be carried out after project approval.

---

Project Highlights

- Web-based department notice management
- Separate HOD / Super Admin and Department Admin roles
- Admin registration approval system
- Admin account enable/disable management
- Admin deletion by HOD
- Password change request and HOD approval
- Profile management for HOD and Admin
- Optional profile photo support
- HOD approval for important Admin profile changes
- Notice creation, editing, and management
- Current and historical notice viewing
- Notice status and expiry information
- Django REST API for current notice retrieval
- Token-based API authentication where configured
- Virtual ESP32 simulator for API communication
- Virtual P10 LED display simulator
- Two P10 panels simulated as one continuous display
- Character-by-character notice animation
- Local server and LAN deployment support
- Git and GitHub version control

---

Current Implementation Status

- Django web application: Implemented
- HOD and Admin workflows: Implemented in the project
- Current Notice REST API: Tested locally
- Virtual ESP32 API communication: Tested locally
- Combined virtual P10 display: Tested locally
- Actual ESP32 hardware integration: Planned
- Physical P10 display integration: Planned
- Cloud deployment: Planned

The virtual simulator demonstrates the software communication flow. It does not verify actual hardware wiring, GPIO signals, LED scanning, brightness, or power consumption.

---

User Roles

HOD / Super Admin

The HOD has administrative control over the system.

Main capabilities:

- Secure login
- Access the HOD dashboard
- Create and manage department notices
- View notice statistics and history
- Approve or reject Admin registrations
- Enable or disable Admin accounts
- Delete Admin accounts
- Review and approve or reject password change requests
- Review important Admin profile change requests
- Manage their own profile

Department Admin

Department Admins can access the functions permitted by the HOD.

Main capabilities:

- Login using registered credentials
- Access the Admin dashboard
- Create and manage notices according to permissions
- View current notices and notice history
- Request password changes
- Manage profile information
- Change or remove profile photos
- Submit important profile changes for HOD approval
- View request status

---

Profile Management

The system supports profile management for both HOD and Admin users.

Profile photos are optional and can be uploaded, changed, or removed.

For Department Admins, important profile information such as full name, email address, mobile number, and department can require HOD approval according to the implemented workflow.

The HOD can manage their own profile directly.

---

Password Change Workflow

Department Admins can submit password change requests through the application.

Workflow:

1. Admin submits a password change request.
2. The request appears on the HOD dashboard.
3. The HOD approves or rejects the request.
4. The password is updated if the request is approved.

This workflow uses application-based approval rather than an email-based password reset.

---

Notice Management

Authorized users can manage department notices through the Django web interface.

Features include:

- Creating and editing notices
- Viewing the current notice
- Viewing notice history
- Managing notice status
- Tracking notice start and expiry times
- Supporting notice priority levels
- Displaying the current notice through the REST API

The API allows a device controller to retrieve the current notice for display.

---

System Architecture

Current Virtual Testing Architecture

HOD / Department Admin
↓
Django Web Application
↓
Django REST API
↓
Virtual ESP32 Simulator
↓
Virtual P10 Panel 1 + Virtual P10 Panel 2
↓
One Continuous Virtual Display

The virtual ESP32 polls the current-notice API at a configured interval. When a new notice is detected, the simulator updates the display.

Both virtual P10 panels represent parts of one large display. The complete notice is not duplicated on both panels.

Planned Physical Hardware Architecture

HOD / Department Admin
↓
Django Server and Database
↓
Authenticated REST API over HTTPS
↓
ESP32 Controller using Wi-Fi / Internet
↓
P10 Panel 1 connected to P10 Panel 2
↓
One Continuous Physical LED Display

The physical ESP32 and P10 panels will be integrated after hardware approval and procurement.

The P10 panels will use a separate suitable 5V high-current power supply. They must not be powered directly from the ESP32.

GSM/SIM800L is not part of the current project implementation. The current design uses server-based IP communication through a REST API.

---

Technology Stack

Backend

- Python
- Django 5.x
- Django ORM
- Django Authentication and Authorization
- Django REST Framework
- SQLite for local development

Frontend

- HTML5
- CSS3
- JavaScript
- Django Templates

Virtual Device Testing

- Python
- Requests library for HTTP communication
- Tkinter for the virtual P10 display
- Token authentication where enabled by the API

Development Tools

- Visual Studio Code
- Git
- GitHub
- Python Virtual Environment

Planned Hardware

- ESP32 development board
- Two P10 LED display panels
- Suitable 5V high-current SMPS
- Data cables and connectors
- Electrical protection and enclosure

---

Project Structure

Smart-Notice-Board/
├── accounts/
├── api/
├── config/
├── notices/
├── services/
├── static/
├── templates/
├── media/
├── tests/
├── virtual_device/
│   ├── config.py
│   ├── requirements.txt
│   ├── test_api.py
│   ├── virtual_esp32.py
│   ├── virtual_p10.py
│   └── README.md
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
└── README.md

The exact structure may vary slightly depending on the current repository version.

---

Installation and Local Setup

1. Clone the repository

git clone https://github.com/Mukesh-Pawar/Smart-Notice-Board.git

2. Open the project directory

cd Smart-Notice-Board

3. Create a virtual environment

python -m venv venv

Activate it on Windows PowerShell:

.\venv\Scripts\Activate.ps1

For Windows Command Prompt:

venv\Scripts\activate.bat

4. Install dependencies

python -m pip install -r requirements.txt

5. Configure environment variables

Review ".env.example" and configure the required environment variables.

Do not commit ".env", passwords, tokens, or secret keys to GitHub.

6. Apply database migrations

python manage.py migrate

7. Create a Django superuser if required

python manage.py createsuperuser

Follow the project's HOD account setup process. A Django superuser may not automatically receive the application's HOD role.

8. Check the project

python manage.py check

9. Run the server

python manage.py runserver

Open the application:

http://127.0.0.1:8000/

---

Run the Virtual ESP32 and P10 Simulator

Keep the Django server running in one terminal.

Open a second terminal and enter the simulator folder:

cd virtual_device

Install the simulator dependency:

python -m pip install -r requirements.txt

Check the API URL in "config.py":

API_URL = "http://127.0.0.1:8000/api/notices/current/"

If the API requires DRF Token authentication, obtain a token through the project's login API and configure it locally:

API_TOKEN = "YOUR_LOCAL_TOKEN"

Never commit a real token or password to GitHub.

Run the simulator:

python virtual_esp32.py

The simulator checks the API at the configured interval. When a new notice is detected, the title and message appear character-by-character across one combined virtual display.

---

API Communication

The current-notice endpoint used by the simulator is:

"GET /api/notices/current/"

The login endpoint configured in the current project is:

"POST /api/auth/login/"

An example current-notice response is:

{
  "success": true,
  "notice": {
    "id": 5,
    "title": "Example Notice",
    "message": "Example Message",
    "priority": "EMERGENCY",
    "start_time": "2026-10-07T02:20:00+05:30",
    "expiry_time": "2026-10-07T03:20:00+05:30",
    "status": "ACTIVE"
  }
}

This is an example response. Actual values depend on the current database and API implementation.

For physical hardware integration, a dedicated device credential or service identity should be used instead of permanently sharing an HOD or Admin login token.

---

LAN Deployment

The Django application can be accessed from other devices on the same local network if the server is configured to accept network connections.

For example, if the server PC has a local IP address of "192.168.1.100", another device may access:

"http://192.168.1.100:8000/"

The server and client must be on a network that allows communication, and the firewall must permit the required port.

For a more stable Windows WSGI deployment, Waitress can be used after configuring the application appropriately:

python -m waitress --listen=0.0.0.0:8000 config.wsgi:application

A DHCP reservation can help the server PC retain the same local IP address.

Do not expose Django's development server directly to the public Internet.

---

Deployment Plan

The current software and virtual hardware simulation have been tested locally.

The combined Django application can be deployed to a suitable hosting service such as Render. A separate Netlify frontend is not mandatory for the current Django Templates-based application.

Before production deployment, configure:

- Production environment variables
- Secure secret key management
- Allowed hosts and HTTPS
- A persistent database such as PostgreSQL
- Static file serving
- Secure API authentication and permissions
- Appropriate logging and error handling
- Dedicated credentials for physical device access

After deployment, the physical ESP32 can retrieve notices through the public HTTPS API once device authentication is configured.

---

Security Considerations

- Keep secret keys, passwords, and tokens private.
- Never commit ".env" or real device credentials.
- Use role-based permissions for HOD and Admin operations.
- Protect API endpoints with appropriate authentication and permissions.
- Use HTTPS for public deployment.
- Prefer dedicated device authentication for the ESP32.
- Configure "ALLOWED_HOSTS" and production security settings correctly.
- Use a persistent production database and maintain appropriate backups.

---

Database

SQLite is suitable for local development and academic demonstration.

For production deployment, the application can be configured to use PostgreSQL or another suitable persistent database.

---

Future Scope

- Physical ESP32 integration
- Physical P10 panels configured as one continuous display
- Scrolling long notices across the full display
- Dedicated device API authentication
- Cloud deployment with HTTPS
- Offline caching of the last valid notice
- Device online/offline status monitoring
- Hardware status monitoring
- Multi-department support
- Optional notification services if required

GSM/SMS functionality is not included in the current server/API-based implementation.

---

Advantages

- Reduces dependence on paper-based notice boards
- Centralizes department notice management
- Provides controlled administrative access
- Supports notice history and status management
- Makes notice data available through a REST API
- Enables virtual testing before purchasing hardware
- Simulates two P10 panels as one continuous display
- Provides a path toward physical IoT integration

---

Academic Project

This engineering project demonstrates web application development, database management, authentication and authorization, REST API communication, virtual device simulation, and planned IoT/embedded display integration.

Department: Electronics & Telecommunication Engineering
College: Alard College of Engineering and Management, Pune

GitHub Repository:
https://github.com/Mukesh-Pawar/Smart-Notice-Board

---

License

This project is licensed under the MIT License. See the "LICENSE" file for the complete license terms.

Copyright (c) 2026 Smart Notice Board Project