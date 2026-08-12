from django.apps import AppConfig


class OrdersConfig(AppConfig):
    name: str = "application.orders.driven_layer.django_orders"
    label: str = "orders"

    def ready(self) -> None:
        from application.orders.composition_root import event_wiring  # noqa: F401
