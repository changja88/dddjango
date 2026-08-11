import pytest


@pytest.mark.django_db
def test_save_round_trips() -> None:
    from application.orders.driven_layer.django_orders.models.order_model import OrderModel

    assert OrderModel.objects.count() == 0
