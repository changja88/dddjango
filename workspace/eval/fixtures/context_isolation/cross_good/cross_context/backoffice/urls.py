from django.contrib import admin
from django.urls import URLPattern, path, re_path

from cross_context.backoffice.suspension.panel import SuspensionPanel

app_name: str = "backoffice"
urlpatterns: list[URLPattern] = [
    path("suspension/", admin.site.admin_view(SuspensionPanel.as_view()), name="suspension"),
    re_path(r"^suspension/(?P<order_id>[0-9]+)/$", view=admin.site.admin_view(SuspensionPanel.as_view()), name="suspension_one"),
]
