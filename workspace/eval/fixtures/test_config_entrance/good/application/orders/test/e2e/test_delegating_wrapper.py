from application.orders.test.e2e._acceptance_helpers import get_order, place_order


def test_place_order_persists(client) -> None:
    response = place_order(client, {"total": "10.00"})
    assert response is not None
    fetched = get_order(client, 1)
    assert fetched is not None
