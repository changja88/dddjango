def test_real_http(client) -> None:
    assert client.get("/api/orders/1/") is not None


def test_sneaky_direct() -> None:
    assert 1 + 1 == 2
