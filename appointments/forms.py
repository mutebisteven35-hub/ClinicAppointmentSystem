from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Appointment, Doctor, DoctorSchedule, Feedback, MedicalHistory, PatientProfile


class PatientRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=80)
    last_name = forms.CharField(max_length=80)
    email = forms.EmailField()
    phone = forms.CharField(max_length=30)
    address = forms.CharField(max_length=200, required=False)
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'phone',
            'address',
            'date_of_birth',
            'password1',
            'password2',
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            PatientProfile.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                address=self.cleaned_data.get('address', ''),
                date_of_birth=self.cleaned_data.get('date_of_birth'),
            )
        return user


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'reason': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = Doctor.objects.filter(is_active=True)

    def clean_date(self):
        date = self.cleaned_data['date']
        if date < timezone.localdate():
            raise ValidationError('Choose today or a future date.')
        return date


class AppointmentStatusForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status', 'admin_note']
        widgets = {
            'admin_note': forms.Textarea(attrs={'rows': 3}),
        }


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['name', 'specialization', 'phone', 'email', 'is_active']


class DoctorScheduleForm(forms.ModelForm):
    class Meta:
        model = DoctorSchedule
        fields = ['doctor', 'day', 'start_time', 'end_time', 'is_available']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }


class MedicalHistoryForm(forms.ModelForm):
    class Meta:
        model = MedicalHistory
        fields = ['patient', 'doctor', 'appointment', 'diagnosis', 'treatment', 'notes', 'visit_date']
        widgets = {
            'visit_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patient'].queryset = User.objects.filter(is_staff=False).order_by('username')
        self.fields['appointment'].queryset = Appointment.objects.order_by('-date', '-time')


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }


class DoctorRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=80, label='First Name')
    last_name = forms.CharField(max_length=80, label='Last Name')
    email = forms.EmailField(label='Email Address')
    specialization = forms.CharField(max_length=120, label='Specialization')
    phone = forms.CharField(max_length=30, label='Phone Number', required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'specialization', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            from .models import Doctor, DoctorProfile
            doctor = Doctor.objects.create(
                name=f"{self.cleaned_data['first_name']} {self.cleaned_data['last_name']}",
                specialization=self.cleaned_data['specialization'],
                phone=self.cleaned_data.get('phone', ''),
                email=self.cleaned_data['email'],
                is_active=True,
            )
            DoctorProfile.objects.create(user=user, doctor=doctor)
        return user


class StaffRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=80, label='First Name')
    last_name = forms.CharField(max_length=80, label='Last Name')
    email = forms.EmailField(label='Email Address')
    staff_role = forms.CharField(max_length=100, label='Role / Position', required=False,
                                  help_text='e.g. Receptionist, Nurse, Administrator')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'staff_role', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.is_staff = True
        if commit:
            user.save()
        return user
