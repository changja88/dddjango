def test_get_order(client) -> None:
    response = client.get("/api/orders/1/")
    assert response is not None
