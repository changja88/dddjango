from application.orders.driving_layer.api.order.order_controller import place_order


def test_place_order_direct(client) -> None:
    client.post("/orders", {"id": place_order.__name__})
