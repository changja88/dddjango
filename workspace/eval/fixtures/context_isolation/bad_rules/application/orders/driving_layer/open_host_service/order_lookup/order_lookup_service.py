from application.orders.domain_layer.order.exception.out_of_stock import OutOfStock


class LookupHelper: ...


def fetch_order(order_id: str, verbose: bool) -> dict:
    try:
        raise OutOfStock()
    except OutOfStock as e:
        code = e.code
        raise OutOfStock()
    return {}

__all__ = ["fetch_order", "OutOfStock"]
