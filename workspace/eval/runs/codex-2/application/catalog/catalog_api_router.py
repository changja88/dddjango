from django.urls import path

from application.catalog.presentation_layer.api.create_order.api_orders import api_orders


urlpatterns = [
    path("orders/", api_orders, name="api-orders"),
]

