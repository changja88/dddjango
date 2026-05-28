"""catalog 앱 외부 HTTP 진입점 — 순수 Django urlpatterns(Ninja Router 등가물 §5.2).

config/urls.py가 include 한다.
"""
from django.urls import path

from application.catalog.presentation_layer.api.place_order.api_order import place_order

urlpatterns = [
    path("orders", place_order, name="place_order"),
]
