"""bad_flows_init_private_sibling — 틀 · `match` 갈래가 없는 ② 꼴 폴더인데 본체 `__init__` 이 형제 클래스
`_PaymentChannel` 을 만들어 `self` 속성에 둔다 — ②′ 부품이다(#661 `_` 부품 클래스 한 줄 · ② 로 두려면
`execute` 안에서 만든다)."""
from __future__ import annotations

from application.orders.application_layer.order.collect_fee.collect_fee_command import CollectFeeCommand
from application.orders.application_layer.order.collect_fee.collect_fee_result import CollectFeeResult

from .payment_channel import _PaymentChannel


class CollectFeeUseCase:
    def __init__(self) -> None:
        self._channel: _PaymentChannel = _PaymentChannel(fee_id=1)

    def execute(self, command: CollectFeeCommand) -> CollectFeeResult:
        sent: bool = self._channel.send(command.target_id)
        return CollectFeeResult(target_id=command.target_id, done=sent)
