from application.orders.domain_layer.order.order import Order


def run() -> None:
    repo = object()
    repo.save(Order())
