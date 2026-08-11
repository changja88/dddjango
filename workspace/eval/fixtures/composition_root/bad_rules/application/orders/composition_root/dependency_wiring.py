from application.orders.application_layer.order.place_order.place_order_use_case import PlaceOrderUseCase


def build_place_order_use_case(kind: str) -> PlaceOrderUseCase:
    if kind == "premium":
        return PlaceOrderUseCase()
    return PlaceOrderUseCase()


def resolve_settings() -> dict:
    return {}
