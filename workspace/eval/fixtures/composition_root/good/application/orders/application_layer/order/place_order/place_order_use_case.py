from application.orders.domain_layer.order.value_object.order_thresholds import OrderThresholds
from application.orders.domain_layer.shared_value_object.language_code import LanguageCode


class PlaceOrderUseCase:
    def __init__(self, *, default_language: LanguageCode, thresholds: OrderThresholds) -> None:
        self._default_language: LanguageCode = default_language
        self._thresholds: OrderThresholds = thresholds

    def execute(self, command: object) -> None:
        return None
