from ninja import NinjaAPI
from application.orders.domain_layer.order.exception.order_not_found import OrderNotFound

api: NinjaAPI = NinjaAPI()


class ErrorSchema:
    pass


def map_order_errors(exc: Exception) -> dict:
    return {}
