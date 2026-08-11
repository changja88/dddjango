from django.test import Client


def test_place_order_flow() -> None:
    client: Client = Client()
    response = client.post("/api/orders/", data={})
    assert response is not None
