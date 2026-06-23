from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Password reset
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html', email_template_name='registration/password_reset_email.html', subject_template_name='registration/password_reset_subject.txt'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # Doctor workspace
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('doctor/appointments/<int:pk>/action/', views.doctor_appointment_action, name='doctor_appointment_action'),

    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('appointments/', views.patient_appointments, name='patient_appointments'),
    path('appointments/book/', views.book_appointment, name='book_appointment'),
    path('appointments/<int:pk>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('doctor-schedules/', views.doctor_schedules, name='doctor_schedules'),
    path('medical-history/', views.patient_medical_history, name='patient_medical_history'),
    path('feedback/', views.patient_feedback, name='patient_feedback'),
    path('feedback/new/', views.feedback_create, name='feedback_create'),

    path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/appointments/', views.staff_appointments, name='staff_appointments'),
    path('staff/appointments/<int:pk>/', views.staff_appointment_detail, name='staff_appointment_detail'),
    path('staff/doctors/', views.staff_doctors, name='staff_doctors'),
    path('staff/doctors/new/', views.staff_doctor_create, name='staff_doctor_create'),
    path('staff/doctors/<int:pk>/edit/', views.staff_doctor_update, name='staff_doctor_update'),
    path('staff/doctors/<int:pk>/delete/', views.staff_doctor_delete, name='staff_doctor_delete'),
    path('staff/schedules/', views.staff_schedules, name='staff_schedules'),
    path('staff/schedules/new/', views.staff_schedule_create, name='staff_schedule_create'),
    path('staff/schedules/<int:pk>/edit/', views.staff_schedule_update, name='staff_schedule_update'),
    path('staff/schedules/<int:pk>/delete/', views.staff_schedule_delete, name='staff_schedule_delete'),
    path('staff/history/', views.staff_medical_history, name='staff_medical_history'),
    path('staff/history/new/', views.staff_history_create, name='staff_history_create'),
    path('staff/history/<int:pk>/edit/', views.staff_history_update, name='staff_history_update'),
    path('staff/feedback/', views.staff_feedback, name='staff_feedback'),
    path('staff/feedback/<int:pk>/read/', views.staff_feedback_mark_read, name='staff_feedback_mark_read'),
]
