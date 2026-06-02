from datetime import time, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Appointment, Doctor, DoctorSchedule, Feedback, PatientProfile


class ClinicFlowTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='admin12345',
            is_staff=True,
            is_superuser=True,
        )
        self.patient = User.objects.create_user(
            username='patient',
            password='patient12345',
            first_name='Demo',
            last_name='Patient',
        )
        PatientProfile.objects.create(user=self.patient, phone='0700000000')
        self.doctor = Doctor.objects.create(name='Amina Namatovu', specialization='General Medicine')
        DoctorSchedule.objects.create(
            doctor=self.doctor,
            day=DoctorSchedule.MONDAY,
            start_time=time(9, 0),
            end_time=time(13, 0),
        )

    def test_patient_can_register(self):
        response = self.client.post(reverse('register'), {
            'username': 'newpatient',
            'first_name': 'New',
            'last_name': 'Patient',
            'email': 'new@clinic.test',
            'phone': '0711111111',
            'address': 'Kampala',
            'date_of_birth': '2001-01-01',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        })

        self.assertRedirects(response, reverse('patient_dashboard'))
        self.assertTrue(User.objects.filter(username='newpatient').exists())
        self.assertTrue(PatientProfile.objects.filter(user__username='newpatient').exists())

    def test_patient_can_book_appointment(self):
        self.client.login(username='patient', password='patient12345')
        appointment_date = timezone.localdate() + timedelta(days=3)

        response = self.client.post(reverse('book_appointment'), {
            'doctor': self.doctor.pk,
            'date': appointment_date.isoformat(),
            'time': '10:00',
            'reason': 'Headache',
        })

        self.assertRedirects(response, reverse('patient_appointments'))
        self.assertEqual(Appointment.objects.count(), 1)
        self.assertEqual(Appointment.objects.first().status, Appointment.PENDING)

    def test_staff_can_update_appointment_status(self):
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=timezone.localdate() + timedelta(days=4),
            time=time(10, 0),
            reason='Checkup',
        )
        self.client.login(username='admin', password='admin12345')

        response = self.client.post(reverse('staff_appointment_detail', args=[appointment.pk]), {
            'status': Appointment.APPROVED,
            'admin_note': 'Approved for visit.',
        })

        self.assertRedirects(response, reverse('staff_appointments'))
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.APPROVED)

    def test_patient_can_cancel_own_appointment(self):
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=timezone.localdate() + timedelta(days=5),
            time=time(11, 0),
            reason='Review',
            status=Appointment.APPROVED,
        )
        self.client.login(username='patient', password='patient12345')

        response = self.client.post(reverse('cancel_appointment', args=[appointment.pk]))

        self.assertRedirects(response, reverse('patient_appointments'))
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.CANCELLED)

    def test_patient_can_send_feedback(self):
        self.client.login(username='patient', password='patient12345')

        response = self.client.post(reverse('feedback_create'), {
            'subject': 'Service',
            'message': 'Good service.',
        })

        self.assertRedirects(response, reverse('patient_feedback'))
        self.assertEqual(Feedback.objects.count(), 1)

# Create your tests here.
