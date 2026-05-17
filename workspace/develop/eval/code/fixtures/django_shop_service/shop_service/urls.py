from __future__ import annotations

from django.http import JsonResponse
from django.urls import path

from apps.orders.api import api


def health(_request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("health/", health),
    path("api/", api.urls),
]
