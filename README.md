Smart Notice Board

GSM-Based Smart Notice Board with Web-Based Department Notice Management System

Smart Notice Board is a web-based department notice management system
developed to digitize the traditional notice board process.

The system provides a centralized platform where the Head of Department
(HOD) and authorized Department Administrators can manage department
notices, user accounts, profile information, password change requests,
and other administrative activities.

The project is designed with future IoT integration in mind. An
ESP32-based controller, SIM800L GSM module, and P10 LED display panels
can be integrated with the Django server to create a complete digital
smart notice board.

------------------------------------------------------------------------

Project Highlights

-   Web-based department notice management
-   Separate HOD and Admin roles
-   HOD as Super Admin
-   Admin registration approval system
-   Admin enable/disable management
-   Admin deletion by HOD
-   Password change request and HOD approval
-   Profile management for HOD and Admin
-   Optional profile photo support
-   Direct profile photo change/remove
-   HOD approval for important Admin profile changes
-   Notice creation and management
-   Current and historical notice viewing
-   Notice status management
-   LAN-based deployment support
-   Waitress WSGI server support
-   Prepared architecture for ESP32 and GSM integration
-   Prepared architecture for P10 LED display integration

------------------------------------------------------------------------

User Roles

HOD / Super Admin

The HOD has complete administrative control over the system.

Main capabilities:

-   Login securely using email and password
-   View the HOD dashboard
-   Manage department notices
-   View notice statistics
-   Approve Admin registrations
-   Reject Admin registrations
-   Enable or disable Admin accounts
-   Permanently delete Admin accounts
-   Review Admin password change requests
-   Approve or reject password change requests
-   Review Admin profile change requests
-   Approve or reject important Admin profile changes
-   Edit own profile directly
-   Change or remove own profile photo
-   Monitor department administration activities

Department Admin

Department Admins have access to the department management functions
allowed by the HOD.

Main capabilities:

-   Login using registered email and password
-   Access Admin dashboard
-   Create and manage notices
-   View current notices
-   View notice history
-   Request password changes
-   Edit profile information
-   Change or remove profile photo directly
-   Request approval for important profile information changes
-   View pending profile change request status

------------------------------------------------------------------------

Profile Management

The system provides profile management for both HOD and Admin users.

Profile photo is optional.

A user can:

-   Upload a profile photo during registration
-   Change the profile photo later
-   Remove the profile photo later

Profile photo operations do not require HOD approval.

For Department Admins, important identity information requires HOD
approval.

Examples include:

-   Full Name
-   Email Address
-   Mobile Number
-   Department

The workflow is:

Admin edits important information | v Profile Change Request | v HOD
Dashboard | +————+ | | v v Approve Reject | | v v Data Updated No Change

HOD can directly modify their own profile information.

------------------------------------------------------------------------

Password Change Workflow

The system uses an approval-based password change workflow for
Department Admins.

Admin requests a new password | v Password Change Request | v HOD
Dashboard | +————+ | | v v Approve Reject | | v v Password Updated
Request Rejected

The system does not depend on an email-based password reset for this
workflow.

------------------------------------------------------------------------

Notice Management

The notice management module allows authorized users to manage
department notices from a centralized web interface.

The system supports:

-   Creating notices
-   Viewing notices
-   Managing active notices
-   Tracking expired notices
-   Viewing notice history
-   Displaying the current notice
-   Managing notice status
-   Showing recent notices

The architecture can later be connected to a physical P10 LED notice
board.

------------------------------------------------------------------------

IoT and Hardware Integration

The project is designed to support an IoT-based smart notice board.

Proposed hardware:

-   ESP32
-   SIM800L GSM module
-   P10 LED display panels
-   Suitable power supply
-   Connecting wires and required interface components

Basic architecture:

Django Server | | Local Network / API | v ESP32 Controller | +——————+ |
| v v P10 Display SIM800L GSM Panels Module

The Django application acts as the central management server, while
ESP32 can work as the hardware controller.

Multiple P10 display panels can be connected to create a larger display
area.

------------------------------------------------------------------------

System Architecture

Users | +———————+ | | v v HOD / Admin Students / Staff | v Django Web
Application | +———————+ | | v v Authentication Notice Management | v
Database | v ESP32 / IoT Integration | v P10 LED Display

------------------------------------------------------------------------

Technology Stack

Backend

-   Python
-   Django 5.x
-   Django Authentication
-   Django ORM
-   SQLite for development
-   Waitress WSGI Server

Frontend

-   HTML5
-   CSS3
-   JavaScript
-   Django Templates

Hardware / IoT

-   ESP32
-   SIM800L
-   P10 LED Display

Development Tools

-   Visual Studio Code
-   Git
-   GitHub
-   Python Virtual Environment

------------------------------------------------------------------------

Project Structure

smart_notice_board/ | +– accounts/ | +– models.py | +– views.py | +–
forms.py | +– urls.py | +– … | +– api/ | +– … | +– config/ | +–
settings.py | +– urls.py | +– wsgi.py | +– … | +– notices/ | +–
models.py | +– views.py | +– services.py | +– … | +– services/ | +– … |
+– static/ | +– css/ | +– js/ | +– templates/ | +– accounts/ | +–
dashboard/ | +– hod/ | +– notices/ | +– registration/ | +– media/ | +–
tests/ | +– manage.py +– requirements.txt +– .env.example +– .gitignore
+– LICENSE +– README.md

------------------------------------------------------------------------

Installation

1. Clone the repository

git clone https://github.com/Mukesh-Pawar/Smart-Notice-Board.git

2. Open the project directory

cd Smart-Notice-Board

3. Create a virtual environment

python -m venv venv

4. Activate the virtual environment

Windows PowerShell:

venv.ps1

Windows CMD:

venv

5. Install dependencies

pip install -r requirements.txt

6. Apply database migrations

python manage.py migrate

7. Create the HOD / Super Admin account

python manage.py createsuperuser

8. Check the project

python manage.py check

9. Run the development server

python manage.py runserver

Open the application in a browser:

http://127.0.0.1:8000/

------------------------------------------------------------------------

LAN Deployment

The Django application can be accessed from other devices connected to
the same local network.

For example, if the department server computer has the IP address:

192.168.1.100

the application can be accessed from another computer or mobile device
using:

http://192.168.1.100:8000/

The server computer and client device must be connected to the same
network.

For a more stable WSGI server, Waitress can be used:

python -m waitress –listen=0.0.0.0:8000 config.wsgi:application

The department computer can therefore work as the local server while
also being used for normal departmental tasks.

------------------------------------------------------------------------

DHCP Reservation

For LAN deployment, DHCP reservation can be configured in the router so
that the server computer receives the same local IP address every time
it connects to the network.

Example:

Server PC | v Router DHCP | v Reserved IP: 192.168.1.100

This makes local access easier because the server address remains
stable.

------------------------------------------------------------------------

Security Considerations

The project includes several Django security mechanisms and access
controls.

These include:

-   Password hashing
-   Session authentication
-   CSRF protection
-   Role-based access control
-   HOD-only management operations
-   Admin account approval
-   Protected dashboard views
-   Allowed host configuration
-   Environment-based configuration support

Sensitive configuration such as secret keys, database credentials, and
other private settings should not be committed to the public repository.

The .env file should remain private.

------------------------------------------------------------------------

Database

SQLite is currently suitable for local development and academic
demonstration.

For larger or production deployments, the project can be migrated to a
database such as PostgreSQL.

------------------------------------------------------------------------

Deployment

The current architecture supports deployment on a department computer
through a local network.

Possible deployment options include:

Local Server

Department PC | +– Django +– SQLite +– Waitress | +– LAN | +– HOD PC +–
Admin PCs +– Mobile Devices +– ESP32

Cloud Deployment

The project can also be adapted for cloud deployment using a suitable
hosting platform and production database.

Cloud deployment can provide remote access outside the department
network.

------------------------------------------------------------------------

Future Scope

The project can be further extended with:

-   Real-time ESP32 integration
-   REST API based communication
-   Multiple P10 display support
-   GSM-based emergency notices
-   Automatic notice scheduling
-   Notice priority levels
-   SMS notification
-   Email notification
-   Student notification system
-   Mobile application
-   PostgreSQL database
-   Cloud deployment
-   HTTPS / SSL
-   Multiple department support
-   Notice analytics
-   Automatic server startup
-   Hardware status monitoring
-   Offline notice caching
-   Remote monitoring of the LED display

------------------------------------------------------------------------

Advantages

-   Reduces paper-based notice management
-   Saves time for department staff
-   Centralizes department notices
-   Provides controlled administrative access
-   Supports multiple Admin users
-   Provides HOD supervision
-   Allows access from computers and mobile devices on the same network
-   Can be integrated with an IoT display
-   Provides a foundation for future GSM communication
-   Easy to extend for multiple departments

------------------------------------------------------------------------

Academic Project

This project is developed as an engineering academic project to
demonstrate the integration of:

-   Web development
-   Database management
-   Authentication and authorization
-   Network-based application deployment
-   IoT concepts
-   Embedded systems
-   GSM communication
-   Digital LED display technology

------------------------------------------------------------------------

Developer

Electronics & Telecommunication Engineering Department
Alard College of Engineering and Management,Pune

Smart Notice Board Project

GitHub: https://github.com/Mukesh-Pawar/Smart-Notice-Board

------------------------------------------------------------------------

License

This project is licensed under the MIT License.

See the LICENSE file for complete license terms.

Copyright (c) 2026 Smart Notice Board Project
