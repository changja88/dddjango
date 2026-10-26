from __future__ import annotations

from application.orders.domain_layer.order.event.refund.refund_closed import RefundClosed
from application.orders.domain_layer.order.event.refund.refund_denied import RefundDenied
from application.orders.domain_layer.order.event.refund.refund_issued import RefundIssued


class RefundOrderUseCase:
    def execute(self, order_id: str, denied: RefundDenied, closed: RefundClosed) -> RefundIssued:
        return RefundIssued(order_id=order_id)
