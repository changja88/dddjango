from application.orders.driven_layer.adapter.persistence.repository.order_repository import DjangoOrderRepository
from application.billing.domain_layer.invoice.invoice import Invoice
from application.orders.application_layer.port.payment_gateway.payment_gateway_port import PaymentGatewayPort


class PlaceOrderUseCase:
    def __init__(self, payment: PaymentGatewayPort) -> None:
        self._payment = payment

    def execute(self, command) -> None:
        with self._uow.unit_of_work():
            self._payment.charge(command)
