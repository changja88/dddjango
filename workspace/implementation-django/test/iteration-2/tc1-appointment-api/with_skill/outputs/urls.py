# ---------------------------------------------------------------------------
# apps/appointments/urls.py
# ---------------------------------------------------------------------------

from rest_framework.routers import DefaultRouter

from apps.appointments.views import AppointmentViewSet

router = DefaultRouter()
router.register("appointments", AppointmentViewSet, basename="appointment")

urlpatterns = router.urls


# ---------------------------------------------------------------------------
# config/urls.py
# ---------------------------------------------------------------------------
#
# from django.contrib import admin
# from django.urls import include, path
#
# urlpatterns = [
#     path("admin/", admin.site.urls),
#     path("api/v1/", include("apps.appointments.urls")),
# ]
