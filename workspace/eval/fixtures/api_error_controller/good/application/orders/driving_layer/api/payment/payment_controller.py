from ninja import Status
from ninja_extra import api_controller, http_get

from application.orders.application_layer.payment.get_payment.get_payment_query import GetPaymentQuery
from application.orders.domain_layer.payment.exception.payment_not_found import PaymentNotFound
from application.orders.driving_layer.api.bc_error_schema import OrdersErrorCode, OrdersErrorSchema
from application.orders.driving_layer.api.payment.schema.schema_out import PaymentOut


@api_controller("/payments")
class PaymentController:
    @http_get("/{payment_id}", response={200: PaymentOut, 404: OrdersErrorSchema})
    def get_payment(self, payment_id: str) -> PaymentOut | Status[OrdersErrorSchema]:
        try:
            result = self._use_case.execute(GetPaymentQuery(payment_id=payment_id))
        except PaymentNotFound:
            return Status(404, OrdersErrorSchema(code=OrdersErrorCode.PAYMENT_NOT_FOUND, message="payment not found"))
        return PaymentOut.model_validate(result)

    @http_get("/{payment_id}/receipt", response={200: PaymentOut, 404: OrdersErrorSchema})
    def get_receipt(self, payment_id: str) -> Status[PaymentOut | OrdersErrorSchema]:
        try:
            result = self._use_case.execute(GetPaymentQuery(payment_id=payment_id))
        except PaymentNotFound:
            return Status(404, OrdersErrorSchema(code=OrdersErrorCode.PAYMENT_NOT_FOUND, message="payment not found"))
        return Status(200, PaymentOut.model_validate(result))
