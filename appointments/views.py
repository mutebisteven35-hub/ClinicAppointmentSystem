from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone

from .forms import (
    AppointmentForm,
    AppointmentStatusForm,
    DoctorForm,
    DoctorScheduleForm,
    FeedbackForm,
    MedicalHistoryForm,
    PatientRegistrationForm,
)
from .models import Appointment, Doctor, DoctorSchedule, Feedback, MedicalHistory


def staff_required(view_func):
    return user_passes_test(lambda user: user.is_authenticated and user.is_staff, login_url='login')(view_func)


def home(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('staff_dashboard')
    if request.user.is_authenticated:
        return redirect('patient_dashboard')
    return render(request, 'appointments/home.html', {
        'doctor_count': Doctor.objects.filter(is_active=True).count(),
        'schedule_count': DoctorSchedule.objects.filter(is_available=True).count(),
    })


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Your patient account has been created.')
            return redirect('patient_dashboard')
    else:
        form = PatientRegistrationForm()
    return render(request, 'appointments/register.html', {'form': form})


@login_required
def patient_dashboard(request):
    if request.user.is_staff:
        return redirect('staff_dashboard')
    today = timezone.localdate()
    appointments = request.user.appointments.filter(date__gte=today)[:5]
    records = request.user.medical_records.all()[:3]
    return render(request, 'appointments/patient_dashboard.html', {
        'appointments': appointments,
        'records': records,
        'pending_count': request.user.appointments.filter(status=Appointment.PENDING).count(),
        'approved_count': request.user.appointments.filter(status=Appointment.APPROVED).count(),
        'history_count': request.user.medical_records.count(),
    })


@login_required
def doctor_schedules(request):
    schedules = DoctorSchedule.objects.select_related('doctor').filter(
        doctor__is_active=True,
        is_available=True,
    )
    return render(request, 'appointments/doctor_schedules.html', {'schedules': schedules})


@login_required
def book_appointment(request):
    if request.user.is_staff:
        return redirect('staff_appointments')
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.status = Appointment.PENDING
            try:
                appointment.full_clean()
            except Exception as exc:
                form.add_error(None, exc)
            else:
                appointment.save()
                messages.success(request, 'Your appointment request has been sent.')
                return redirect('patient_appointments')
    else:
        form = AppointmentForm()
    return render(request, 'appointments/book_appointment.html', {'form': form})


@login_required
def patient_appointments(request):
    if request.user.is_staff:
        return redirect('staff_appointments')
    appointments = request.user.appointments.select_related('doctor')
    return render(request, 'appointments/patient_appointments.html', {'appointments': appointments})


@login_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, patient=request.user)
    if request.method == 'POST':
        if appointment.status in [Appointment.PENDING, Appointment.APPROVED]:
            appointment.status = Appointment.CANCELLED
            appointment.save(update_fields=['status', 'updated_at'])
            messages.success(request, 'Appointment cancelled.')
        else:
            messages.warning(request, 'Only pending or approved appointments can be cancelled.')
    return redirect('patient_appointments')


@login_required
def patient_medical_history(request):
    if request.user.is_staff:
        return redirect('staff_medical_history')
    records = request.user.medical_records.select_related('doctor', 'appointment')
    return render(request, 'appointments/medical_history.html', {'records': records})


@login_required
def patient_feedback(request):
    if request.user.is_staff:
        return redirect('staff_feedback')
    feedback = request.user.feedback_messages.all()
    return render(request, 'appointments/feedback_list.html', {'feedback': feedback})


@login_required
def feedback_create(request):
    if request.user.is_staff:
        return redirect('staff_feedback')
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.patient = request.user
            feedback.save()
            messages.success(request, 'Your feedback has been sent.')
            return redirect('patient_feedback')
    else:
        form = FeedbackForm()
    return render(request, 'appointments/feedback_form.html', {'form': form})


@staff_required
def staff_dashboard(request):
    today = timezone.localdate()
    pending = Appointment.objects.filter(status=Appointment.PENDING).select_related('patient', 'doctor')[:8]
    status_counts = Appointment.objects.values('status').annotate(total=Count('id'))
    return render(request, 'appointments/staff/dashboard.html', {
        'pending': pending,
        'pending_count': Appointment.objects.filter(status=Appointment.PENDING).count(),
        'today_count': Appointment.objects.filter(date=today).count(),
        'patient_count': User.objects.filter(is_staff=False).count(),
        'doctor_count': Doctor.objects.count(),
        'unread_feedback_count': Feedback.objects.filter(is_read=False).count(),
        'status_counts': status_counts,
    })


@staff_required
def staff_appointments(request):
    status = request.GET.get('status', '')
    appointments = Appointment.objects.select_related('patient', 'doctor')
    if status:
        appointments = appointments.filter(status=status)
    return render(request, 'appointments/staff/appointments.html', {
        'appointments': appointments,
        'status': status,
        'status_choices': Appointment.STATUS_CHOICES,
    })


@staff_required
def staff_appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment.objects.select_related('patient', 'doctor'), pk=pk)
    if request.method == 'POST':
        form = AppointmentStatusForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appointment updated.')
            return redirect('staff_appointments')
    else:
        form = AppointmentStatusForm(instance=appointment)
    return render(request, 'appointments/staff/appointment_detail.html', {
        'appointment': appointment,
        'form': form,
    })


@staff_required
def staff_doctors(request):
    doctors = Doctor.objects.annotate(schedule_count=Count('schedules'), appointment_count=Count('appointments'))
    return render(request, 'appointments/staff/doctors.html', {'doctors': doctors})


@staff_required
def staff_doctor_create(request):
    return _save_form(request, DoctorForm, 'appointments/staff/doctor_form.html', 'staff_doctors', 'Doctor saved.')


@staff_required
def staff_doctor_update(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    return _save_form(request, DoctorForm, 'appointments/staff/doctor_form.html', 'staff_doctors', 'Doctor updated.', instance=doctor)


@staff_required
def staff_doctor_delete(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        doctor.delete()
        messages.success(request, 'Doctor deleted.')
        return redirect('staff_doctors')
    return render(request, 'appointments/staff/confirm_delete.html', {'object': doctor, 'cancel_url': reverse_lazy('staff_doctors')})


@staff_required
def staff_schedules(request):
    schedules = DoctorSchedule.objects.select_related('doctor')
    return render(request, 'appointments/staff/schedules.html', {'schedules': schedules})


@staff_required
def staff_schedule_create(request):
    return _save_form(request, DoctorScheduleForm, 'appointments/staff/schedule_form.html', 'staff_schedules', 'Schedule saved.')


@staff_required
def staff_schedule_update(request, pk):
    schedule = get_object_or_404(DoctorSchedule, pk=pk)
    return _save_form(request, DoctorScheduleForm, 'appointments/staff/schedule_form.html', 'staff_schedules', 'Schedule updated.', instance=schedule)


@staff_required
def staff_schedule_delete(request, pk):
    schedule = get_object_or_404(DoctorSchedule, pk=pk)
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, 'Schedule deleted.')
        return redirect('staff_schedules')
    return render(request, 'appointments/staff/confirm_delete.html', {'object': schedule, 'cancel_url': reverse_lazy('staff_schedules')})


@staff_required
def staff_medical_history(request):
    records = MedicalHistory.objects.select_related('patient', 'doctor', 'appointment')
    return render(request, 'appointments/staff/history.html', {'records': records})


@staff_required
def staff_history_create(request):
    return _save_form(request, MedicalHistoryForm, 'appointments/staff/history_form.html', 'staff_medical_history', 'Medical history saved.')


@staff_required
def staff_history_update(request, pk):
    record = get_object_or_404(MedicalHistory, pk=pk)
    return _save_form(request, MedicalHistoryForm, 'appointments/staff/history_form.html', 'staff_medical_history', 'Medical history updated.', instance=record)


@staff_required
def staff_feedback(request):
    feedback = Feedback.objects.select_related('patient')
    return render(request, 'appointments/staff/feedback.html', {'feedback': feedback})


@staff_required
def staff_feedback_mark_read(request, pk):
    feedback = get_object_or_404(Feedback, pk=pk)
    if request.method == 'POST':
        feedback.is_read = True
        feedback.save(update_fields=['is_read'])
        messages.success(request, 'Feedback marked as read.')
    return redirect('staff_feedback')


def _save_form(request, form_class, template_name, redirect_name, success_message, instance=None):
    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, success_message)
            return redirect(redirect_name)
    else:
        form = form_class(instance=instance)
    return render(request, template_name, {'form': form, 'object': instance})

# Create your views here.


def doctor_required(view_func):
    """Allow access only to users who have a linked DoctorProfile."""
    from .models import DoctorProfile

    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        if not hasattr(request.user, 'doctor_profile'):
            messages.error(request, 'You do not have a doctor account.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


@doctor_required
def doctor_dashboard(request):
    from .models import DoctorProfile
    doctor = request.user.doctor_profile.doctor
    pending = Appointment.objects.filter(doctor=doctor, status=Appointment.PENDING).select_related('patient').order_by('date', 'time')
    today_appointments = Appointment.objects.filter(doctor=doctor, date=timezone.localdate(), status=Appointment.APPROVED).select_related('patient')
    return render(request, 'appointments/doctor/dashboard.html', {
        'doctor': doctor,
        'pending': pending,
        'pending_count': pending.count(),
        'today_count': today_appointments.count(),
        'today_appointments': today_appointments,
        'total_patients': Appointment.objects.filter(doctor=doctor, status=Appointment.APPROVED).values('patient').distinct().count(),
    })


@doctor_required
def doctor_appointments(request):
    doctor = request.user.doctor_profile.doctor
    status = request.GET.get('status', '')
    appointments = Appointment.objects.filter(doctor=doctor).select_related('patient')
    if status:
        appointments = appointments.filter(status=status)
    return render(request, 'appointments/doctor/appointments.html', {
        'appointments': appointments,
        'status': status,
        'status_choices': Appointment.STATUS_CHOICES,
        'doctor': doctor,
    })


@doctor_required
def doctor_appointment_action(request, pk):
    doctor = request.user.doctor_profile.doctor
    appointment = get_object_or_404(Appointment, pk=pk, doctor=doctor)
    if request.method == 'POST':
        action = request.POST.get('action')
        note = request.POST.get('admin_note', '').strip()
        if action == 'approve' and appointment.status == Appointment.PENDING:
            appointment.status = Appointment.APPROVED
            appointment.admin_note = note
            appointment.save(update_fields=['status', 'admin_note', 'updated_at'])
            messages.success(request, 'Appointment approved.')
        elif action == 'cancel' and appointment.status in [Appointment.PENDING, Appointment.APPROVED]:
            appointment.status = Appointment.CANCELLED
            appointment.admin_note = note
            appointment.save(update_fields=['status', 'admin_note', 'updated_at'])
            messages.success(request, 'Appointment cancelled.')
        elif action == 'complete' and appointment.status == Appointment.APPROVED:
            appointment.status = Appointment.COMPLETED
            appointment.admin_note = note
            appointment.save(update_fields=['status', 'admin_note', 'updated_at'])
            messages.success(request, 'Appointment marked as completed.')
        else:
            messages.warning(request, 'Invalid action or appointment state.')
    return redirect('doctor_appointments')
