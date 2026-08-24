"""#197 경계(음성) — factory 호출형 with 라도 읽기 전용이면 red(kkebi reconcile 판형).

«with uow» 진입 자체는 쓰기-사용이 아니다 — 도달 범위에 save/remove/after_commit/escape 가 0.
"""
from __future__ import annotations

from collections.abc import Callable

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork


class ReconcileOrderUseCase:
    def __init__(self, unit_of_work_factory: Callable[[], OrdersUnitOfWork]) -> None:
        self._unit_of_work_factory: Callable[[], OrdersUnitOfWork] = unit_of_work_factory

    def execute(self, order_id: str) -> str:
        with self._unit_of_work_factory() as unit_of_work:
            order = unit_of_work.repository.get(order_id)
        return "matched" if order is not None else "missing"
