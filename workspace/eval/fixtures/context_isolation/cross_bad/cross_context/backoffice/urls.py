from django.contrib import admin
from django.urls import URLPattern, include, path, re_path

from cross_context.backoffice.suspension.panel import SuspensionPanel

app_name: str = "backoffice"
_spare: list[URLPattern] = [path("spare/", SuspensionPanel.as_view())]
urlpatterns: list[URLPattern] = [
    path("suspension/", admin.site.admin_view(SuspensionPanel.as_view()), name="suspension"),
    path("bare/", SuspensionPanel.as_view()),
    path("nested/", include("cross_context.backoffice.suspension.feature.raw_routes")),
] + [path("plus/", SuspensionPanel.as_view())]
urlpatterns += [path("augmented/", SuspensionPanel.as_view())]
urlpatterns.append(path("appended/", SuspensionPanel.as_view()))
urlpatterns.extend(_spare)
urlpatterns.append(re_path(r"^keyword/$", view=SuspensionPanel.as_view()))
