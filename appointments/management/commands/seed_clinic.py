from datetime import date, time, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from appointments.models import Appointment, Doctor, DoctorSchedule, Feedback, MedicalHistory, PatientProfile


class Command(BaseCommand):
    help = 'Create demo users, doctors, schedules, appointments, medical records, and feedback.'

    def handle(self, *args, **options):
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@clinic.test',
                'first_name': 'Clinic',
                'last_name': 'Admin',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        if created:
            admin.set_password('admin12345')
            admin.save()

        patient, created = User.objects.get_or_create(
            username='patient',
            defaults={
                'email': 'patient@clinic.test',
                'first_name': 'Demo',
                'last_name': 'Patient',
            },
        )
        if created:
            patient.set_password('patient12345')
            patient.save()
        PatientProfile.objects.get_or_create(
            user=patient,
            defaults={
                'phone': '0700000000',
                'address': 'Kampala',
                'date_of_birth': date(2000, 1, 1),
            },
        )

        doctors = [
            ('Amina Namatovu', 'General Medicine', '0751000101', 'amina@clinic.test'),
            ('Peter Okello', 'Pediatrics', '0751000102', 'peter@clinic.test'),
            ('Sarah Kato', 'Dental Care', '0751000103', 'sarah@clinic.test'),
        ]
        doctor_objects = []
        for name, specialization, phone, email in doctors:
            doctor, _ = Doctor.objects.get_or_create(
                name=name,
                defaults={
                    'specialization': specialization,
                    'phone': phone,
                    'email': email,
                },
            )
            doctor_objects.append(doctor)

        schedules = [
            (doctor_objects[0], DoctorSchedule.MONDAY, time(9, 0), time(13, 0)),
            (doctor_objects[0], DoctorSchedule.WEDNESDAY, time(14, 0), time(17, 0)),
            (doctor_objects[1], DoctorSchedule.TUESDAY, time(8, 30), time(12, 30)),
            (doctor_objects[1], DoctorSchedule.THURSDAY, time(13, 0), time(16, 30)),
            (doctor_objects[2], DoctorSchedule.FRIDAY, time(9, 0), time(15, 0)),
        ]
        for doctor, day, start, end in schedules:
            DoctorSchedule.objects.get_or_create(
                doctor=doctor,
                day=day,
                start_time=start,
                end_time=end,
                defaults={'is_available': True},
            )

        appointment, _ = Appointment.objects.get_or_create(
            patient=patient,
            doctor=doctor_objects[0],
            date=date.today() + timedelta(days=2),
            time=time(10, 0),
            defaults={
                'reason': 'General consultation and checkup',
                'status': Appointment.PENDING,
            },
        )

        MedicalHistory.objects.get_or_create(
            patient=patient,
            doctor=doctor_objects[1],
            diagnosis='Mild flu',
            visit_date=date.today() - timedelta(days=14),
            defaults={
                'appointment': None,
                'treatment': 'Rest, fluids, and paracetamol',
                'notes': 'Patient recovered well after the visit.',
            },
        )

        Feedback.objects.get_or_create(
            patient=patient,
            subject='Booking process',
            defaults={'message': 'The online booking process is easy to follow.'},
        )

        self.stdout.write(self.style.SUCCESS('Demo clinic data created.'))
        self.stdout.write('Admin login: admin / admin12345')
        self.stdout.write('Patient login: patient / patient12345')
