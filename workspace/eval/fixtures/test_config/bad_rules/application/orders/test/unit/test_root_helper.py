from tests.helpers import make_order_id


def test_order_id_shape() -> None:
    assert make_order_id().startswith("order-")
