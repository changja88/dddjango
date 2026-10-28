from __future__ import annotations

from .order_pricing_table import piece_0
from .payment_channel import _PaymentChannel
from .payment_declined import PaymentDeclined


class PlaceOrderUseCase:
    def execute(self, command: "PlaceOrderCommand") -> None:
        piece_0()
        channel: _PaymentChannel = _PaymentChannel(order_id=1)
        if not channel.send(amount=100):
            raise PaymentDeclined(order_id=1)
