"""ok_frame_publish_after_commit — 작업 단위 구간은 본체((i) 꼴) · 발행 도구는 틀 · 본체가 틀의 발행 메서드를
`after_commit(self._frame.publish_paid)` 로 커밋 뒤에 등록한다(#541 0 줄 — 틀 파일만 봐서는 등록이 안 보인다)."""
from __future__ import annotations

from application.orders.application_layer.order.pay_order.pay_order_command import PayOrderCommand
from application.orders.application_layer.order.pay_order.pay_order_result import PayOrderResult
from application.orders.application_layer.port.event_publisher.event_publisher_port import EventPublisherPort
from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order_repository import OrderRepository

from .card_charge import CardCharge
from .pay_order_frame import PayOrderFrame


class PayOrderUseCase:
    def __init__(self, order_repository: OrderRepository, unit_of_work: OrdersUnitOfWork,
                 event_publisher: EventPublisherPort) -> None:
        self._unit_of_work: OrdersUnitOfWork = unit_of_work
        self._frame: PayOrderFrame = PayOrderFrame(order_repository, event_publisher)
        self._card_charge: CardCharge = CardCharge(frame=self._frame)

    def execute(self, command: PayOrderCommand) -> PayOrderResult:
        with self._unit_of_work:
            self._card_charge.charge(command.order_id)
            self._unit_of_work.after_commit(self._frame.publish_paid)
        return PayOrderResult(order_id=command.order_id)
