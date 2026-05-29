from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "application.orders.infra_layer.django_orders"
    label = "orders"
