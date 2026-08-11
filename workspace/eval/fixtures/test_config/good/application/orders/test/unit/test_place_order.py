from application.orders.application_layer.order.place_order.place_order_use_case import PlaceOrderUseCase
from application.orders.test.fake.fake_order_repository import FakeOrderRepository


def test_place_order_uses_fake_repository() -> None:
    use_case: PlaceOrderUseCase = PlaceOrderUseCase(FakeOrderRepository())
    assert use_case is not None
