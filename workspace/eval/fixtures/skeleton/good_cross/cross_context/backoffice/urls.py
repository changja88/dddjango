from django.contrib import admin
from django.urls import path, URLPattern

from cross_context.backoffice.suspension.panel import SuspensionPanel

app_name: str = "backoffice"
urlpatterns: list[URLPattern] = [
    path("suspension/", admin.site.admin_view(SuspensionPanel.as_view()), name="suspension"),
]
