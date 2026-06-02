from django.contrib import admin

from .models import Appointment, Doctor, DoctorSchedule, Feedback, MedicalHistory, PatientProfile


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'address', 'date_of_birth')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone')


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization', 'phone', 'email', 'is_active')
    list_filter = ('specialization', 'is_active')
    search_fields = ('name', 'specialization')


@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'day', 'start_time', 'end_time', 'is_available')
    list_filter = ('day', 'is_available', 'doctor')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'time', 'status', 'created_at')
    list_filter = ('status', 'doctor', 'date')
    search_fields = ('patient__username', 'patient__first_name', 'patient__last_name', 'doctor__name')


@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'diagnosis', 'visit_date')
    list_filter = ('doctor', 'visit_date')
    search_fields = ('patient__username', 'diagnosis', 'treatment')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('subject', 'patient', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('subject', 'message', 'patient__username')

# Register your models here.
