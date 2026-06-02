from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    phone = models.CharField(max_length=30)
    address = models.CharField(max_length=200, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Doctor(models.Model):
    name = models.CharField(max_length=120)
    specialization = models.CharField(max_length=120)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'Dr. {self.name} - {self.specialization}'


class DoctorSchedule(models.Model):
    MONDAY = 'Monday'
    TUESDAY = 'Tuesday'
    WEDNESDAY = 'Wednesday'
    THURSDAY = 'Thursday'
    FRIDAY = 'Friday'
    SATURDAY = 'Saturday'
    SUNDAY = 'Sunday'
    DAY_CHOICES = [
        (MONDAY, MONDAY),
        (TUESDAY, TUESDAY),
        (WEDNESDAY, WEDNESDAY),
        (THURSDAY, THURSDAY),
        (FRIDAY, FRIDAY),
        (SATURDAY, SATURDAY),
        (SUNDAY, SUNDAY),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedules')
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['doctor__name', 'day', 'start_time']

    def clean(self):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError('End time must be after start time.')

    def __str__(self):
        return f'{self.doctor} on {self.day}, {self.start_time:%H:%M}-{self.end_time:%H:%M}'


class Appointment(models.Model):
    PENDING = 'Pending'
    APPROVED = 'Approved'
    CANCELLED = 'Cancelled'
    COMPLETED = 'Completed'
    STATUS_CHOICES = [
        (PENDING, PENDING),
        (APPROVED, APPROVED),
        (CANCELLED, CANCELLED),
        (COMPLETED, COMPLETED),
    ]

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-time']

    def clean(self):
        if self.date and self.date < timezone.localdate():
            raise ValidationError({'date': 'Appointment date cannot be in the past.'})

        active_statuses = [self.PENDING, self.APPROVED]
        clash = Appointment.objects.filter(
            doctor=self.doctor,
            date=self.date,
            time=self.time,
            status__in=active_statuses,
        ).exclude(pk=self.pk)
        if clash.exists() and self.status in active_statuses:
            raise ValidationError('This doctor already has an active appointment at that time.')

    def __str__(self):
        return f'{self.patient.username} with {self.doctor.name} on {self.date} at {self.time:%H:%M}'


class MedicalHistory(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name='medical_records')
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='medical_history',
    )
    diagnosis = models.CharField(max_length=200)
    treatment = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    visit_date = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-visit_date', '-created_at']

    def __str__(self):
        return f'{self.patient.username} - {self.diagnosis} ({self.visit_date})'


class Feedback(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback_messages')
    subject = models.CharField(max_length=150)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.subject} from {self.patient.username}'

# Create your models here.
