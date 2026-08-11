import pytest

from application.orders.test.factories.order_factory import OrderModelFactory


@pytest.mark.django_db
def test_order_saved() -> None:
    order = OrderModelFactory()
    assert order is not None
