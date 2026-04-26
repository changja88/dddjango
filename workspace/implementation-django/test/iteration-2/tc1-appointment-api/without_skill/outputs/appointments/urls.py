from django.urls import path

from . import views

app_name = "appointments"

urlpatterns = [
    # Patient / Doctor 조회
    path("patients/", views.PatientListView.as_view(), name="patient-list"),
    path("doctors/", views.DoctorListView.as_view(), name="doctor-list"),
    # Appointment CRUD
    path(
        "appointments/",
        views.AppointmentListCreateView.as_view(),
        name="appointment-list-create",
    ),
    path(
        "appointments/<int:pk>/",
        views.AppointmentDetailView.as_view(),
        name="appointment-detail",
    ),
    # 상태 전이 액션
    path(
        "appointments/<int:pk>/confirm/",
        views.AppointmentConfirmView.as_view(),
        name="appointment-confirm",
    ),
    path(
        "appointments/<int:pk>/complete/",
        views.AppointmentCompleteView.as_view(),
        name="appointment-complete",
    ),
    path(
        "appointments/<int:pk>/cancel/",
        views.AppointmentCancelView.as_view(),
        name="appointment-cancel",
    ),
]
