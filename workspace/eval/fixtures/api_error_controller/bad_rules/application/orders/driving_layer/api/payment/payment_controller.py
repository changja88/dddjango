from ninja import Status
from ninja_extra import api_controller, http_get

from application.orders.driving_layer.api.payment.schema.schema_out import PaymentOut, PaymentErrorOut


@api_controller("/payments")
class PaymentController:
    @http_get("/{payment_id}", response={200: PaymentOut, 404: PaymentErrorOut})
    def get_payment(self, payment_id: str) -> Status[PaymentOut] | Status[PaymentErrorOut]:
        return Status(200, PaymentOut(kind="card", payment_id=payment_id))
