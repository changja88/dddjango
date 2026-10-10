from application.orders.application_layer.order.place_order.place_order_use_case import PlaceOrderUseCase
from application.orders.composition_root import wiring_material


def build_place_order_use_case() -> PlaceOrderUseCase:
    return PlaceOrderUseCase(
        default_language=wiring_material.default_language(),
        thresholds=wiring_material.order_thresholds(),
    )
