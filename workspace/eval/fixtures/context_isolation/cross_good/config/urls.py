from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path

urlpatterns: list[URLPattern | URLResolver] = [
    path("admin/backoffice/", include("cross_context.backoffice.urls")),
    path("ops/backoffice/", include(("cross_context.backoffice.urls", "backoffice"), namespace="ops")),
    path("admin/", admin.site.urls),
]
