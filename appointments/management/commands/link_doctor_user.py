"""
Management command to link a Django User to a Doctor record.

Usage (run in PythonAnywhere bash console):
    python manage.py link_doctor_user --username <username> --doctor_id <id>

To create a user for the doctor first:
    python manage.py createsuperuser   # or create via admin

To list available doctors:
    python manage.py link_doctor_user --list
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from appointments.models import Doctor, DoctorProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Link a Django user to a Doctor record so they can use the doctor workspace.'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username of the Django user')
        parser.add_argument('--doctor_id', type=int, help='ID of the Doctor record')
        parser.add_argument('--list', action='store_true', help='List all doctors and their IDs')

    def handle(self, *args, **options):
        if options['list']:
            doctors = Doctor.objects.all()
            if not doctors:
                self.stdout.write('No doctors found.')
                return
            self.stdout.write('\nAvailable Doctors:')
            for d in doctors:
                linked = '✅ linked' if hasattr(d, 'profile') else '❌ not linked'
                self.stdout.write(f'  ID={d.pk}  Name={d.name}  Specialization={d.specialization}  [{linked}]')
            return

        username = options.get('username')
        doctor_id = options.get('doctor_id')

        if not username or not doctor_id:
            self.stderr.write('Please provide both --username and --doctor_id, or use --list.')
            return

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stderr.write(f'User "{username}" not found.')
            return

        try:
            doctor = Doctor.objects.get(pk=doctor_id)
        except Doctor.DoesNotExist:
            self.stderr.write(f'Doctor with ID {doctor_id} not found.')
            return

        profile, created = DoctorProfile.objects.get_or_create(user=user, defaults={'doctor': doctor})
        if not created:
            profile.doctor = doctor
            profile.save()

        self.stdout.write(self.style.SUCCESS(
            f'✅ User "{username}" is now linked to Dr. {doctor.name}.'
        ))
