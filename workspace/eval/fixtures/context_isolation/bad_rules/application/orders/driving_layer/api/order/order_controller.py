from ninja_extra import api_controller
from application.orders.application_layer.port.payment_gateway.payment_gateway_port import PaymentGatewayPort
from application.orders.driven_layer.adapter.persistence.repository.order_repository import DjangoOrderRepository
from application.orders.domain_layer.order.order import Order
from application.billing.driving_layer.api.invoice.invoice_controller import InvoiceController
from application.billing.composition_root.dependency_wiring import wire


@api_controller("/orders")
class OrderController: ...
