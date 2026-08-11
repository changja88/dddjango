from application.orders.application_layer.order.place_order.place_order_use_case import PlaceOrderUseCase


def test_place_order_direct() -> None:
    assert PlaceOrderUseCase is not None
