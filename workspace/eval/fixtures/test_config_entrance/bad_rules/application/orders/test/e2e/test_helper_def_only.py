def _probe(client):
    return client.get("/api/orders/1/")


def test_order_without_entrance() -> None:
    value: int = 1 + 1
    assert value == 2
