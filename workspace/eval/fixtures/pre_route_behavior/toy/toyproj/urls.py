from django.urls import path

import toyproj.routes  # noqa: F401 — 경로를 루트 API 에 단다
from toyproj.api import api, api2, apib
from toyproj.extra_api import api3

urlpatterns = [path("api/", api.urls), path("api2/", api2.urls), path("api3/", api3.urls), path("apib/", apib.urls)]
