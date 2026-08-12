from application.orders.application_layer.order.place_order.place_order_use_case import (
    PlaceOrderUseCase,
)


def test_place_order_via_use_case(client) -> None:
    client.post("/login/", data={})
    result = PlaceOrderUseCase().execute(total="10.00")
    assert result is not None
