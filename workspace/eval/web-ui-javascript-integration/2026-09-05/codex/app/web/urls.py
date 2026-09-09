from django.urls import URLResolver, include, path

urlpatterns: list[URLResolver] = [path("", include("web.lab.urls"))]
