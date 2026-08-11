from application.orders.application_layer.port.payment_gateway.payment_gateway_port import PaymentGatewayPort


class BillingPaymentAdapter(PaymentGatewayPort):
    def charge(self, command) -> None: ...
