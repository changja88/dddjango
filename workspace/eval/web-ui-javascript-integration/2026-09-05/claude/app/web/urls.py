from django.urls import include, path

urlpatterns: list = [path("lab/", include("web.lab.urls"))]
