import celery
from django.apps import AppConfig
from application.orders.composition_root import event_wiring


def on_saved(sender, **kwargs):
    pass


class OrdersConfig(AppConfig):
    name = "django_orders"

    def ready(self) -> None:
        from application.orders.composition_root import event_wiring
        count = self.get_model("Order").objects.count()
