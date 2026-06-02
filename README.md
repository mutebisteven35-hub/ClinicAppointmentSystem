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

## Deploy on PythonAnywhere

Open a PythonAnywhere Bash console and run:

```bash
git clone https://github.com/mutebisteven35-hub/ClinicAppointmentSystem.git
cd ClinicAppointmentSystem
mkvirtualenv --python=/usr/bin/python3.10 clinic-env
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_clinic
python manage.py collectstatic --noinput
```

On the PythonAnywhere **Web** tab:

1. Click **Add a new web app**.
2. Choose **Manual configuration**, then choose the same Python version used for the virtualenv.
3. Set **Source code** and **Working directory** to:

```text
/home/YOUR_USERNAME/ClinicAppointmentSystem
```

4. Set **Virtualenv** to:

```text
/home/YOUR_USERNAME/.virtualenvs/clinic-env
```

5. In **Static files**, add:

```text
URL: /static/
Directory: /home/YOUR_USERNAME/ClinicAppointmentSystem/staticfiles
```

6. Open the WSGI file link and replace its contents with:

```python
import os
import sys

path = '/home/YOUR_USERNAME/ClinicAppointmentSystem'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'clinic_project.settings'
os.environ['DEBUG'] = 'False'
os.environ['SECRET_KEY'] = 'replace-this-with-a-long-random-secret-key'
os.environ['ALLOWED_HOSTS'] = 'YOUR_USERNAME.pythonanywhere.com,.pythonanywhere.com'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Replace `YOUR_USERNAME` with your PythonAnywhere username, then click **Reload** on the Web tab.

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
