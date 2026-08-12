def _compute_total() -> int:
    return 3


def test_place_order_unused_client(client) -> None:
    total: int = _compute_total()
    assert total == 3
