from typing import Protocol

from application.orders.application_layer.payment.get_payment.get_payment_query import GetPaymentQuery


class GetPaymentUseCase(Protocol):
    def execute(self, query: GetPaymentQuery) -> object: ...
