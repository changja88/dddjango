from django.urls import URLPattern, path

from cross_context.backoffice.suspension.panel import SuspensionPanel

urlpatterns: list[URLPattern] = [path("open/", SuspensionPanel.as_view())]
