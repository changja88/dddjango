from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path
from django.utils.module_loading import import_string

from cross_context.backoffice.suspension.panel import SuspensionPanel

urlpatterns: list[URLPattern | URLResolver] = [
    path("admin/backoffice/", include("cross_context.backoffice.urls")),
    path("ops/", include("cross_context.backoffice.suspension.feature.raw_routes")),
    path("ops/app/", include("cross_context.backoffice")),
    path("ops/suspension/", SuspensionPanel.as_view()),
    path("ops/dynamic/", import_string("cross_context.backoffice.suspension.panel.SuspensionPanel").as_view()),
    path("admin/", admin.site.urls),
]
