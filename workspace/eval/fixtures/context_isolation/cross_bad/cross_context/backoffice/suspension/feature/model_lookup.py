from django.apps import apps


def order_model() -> object:
    return apps.get_model("orders", "Order")
