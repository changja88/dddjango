"""#195 0 줄 — 함께 커밋 승인 꼴 S: 루트 메서드 호출을 받은 둘을 키 정렬 글자 고리로 CAS 저장(반복 변수도 받은 것)."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository


class MovePairSortedUseCase:
    def __init__(self, repository: OrderRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._repository: OrderRepository = repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, order_id: str, other_id: str) -> None:
        # joint-commit: 함께 order×2  잠금 order(order_id)  불변식 옮긴 요청은 정확히 한 주문에만 있다
        with self._unit_of_work:
            source: Order = self._repository.get(order_id)
            target: Order = self._repository.get(other_id)
            source.cancel()
            target.move_to(source.order_id)
            order: Order
            for order in sorted((source, target), key=lambda item: item.order_id):
                if not self._repository.save_with_version_guard(order):
                    raise RuntimeError(order.order_id)
