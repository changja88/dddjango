from django.urls import path

from application.orders.presentation_layer.api.create_order.api_orders import (
    create_order_api,
)


urlpatterns = [
    path("", create_order_api, name="create-order"),
]
