# Medical Clinic Appointment Booking System

This is a Django-only clinic appointment booking system using Django templates and SQLite.

## Main Features

- Patient registration and login
- Appointment booking
- Doctor schedule viewing
- Appointment approval, cancellation, and completion
- Staff management dashboard
- Doctor and schedule CRUD
- Patient medical history records
- Contact and feedback form

## Run Locally

```powershell
cd "C:\Users\USER\OneDrive\Desktop\SDP\ClinicAppointmentSystem"
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_clinic
.\.venv\Scripts\python.exe manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Demo Logins

- Admin: `admin` / `admin12345`
- Patient: `patient` / `patient12345`

## Deployment Preparation

Set these environment variables before deployment:

```powershell
$env:SECRET_KEY="use-a-strong-secret-key"
$env:DEBUG="False"
$env:ALLOWED_HOSTS="your-domain.com,127.0.0.1"
.\.venv\Scripts\python.exe manage.py collectstatic
```

After setting the environment variables, run:

```powershell
.\.venv\Scripts\python.exe manage.py check --deploy
```
