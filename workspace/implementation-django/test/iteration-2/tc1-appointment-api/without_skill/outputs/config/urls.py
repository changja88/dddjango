"""
Root URL configuration for appointment_project.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("appointments.urls")),
]
