from application.orders.application_layer.order.count_order.count_order_use_case.count_order_failure import _CountOrderFailure


def test_failure_keeps_category() -> None:
    assert _CountOrderFailure("empty").category == "empty"
