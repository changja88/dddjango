"""#197 측정 정밀화(2026-08-25) 경계 — factory 호출형 with + repository escape(kkebi import 판형).

쓰기는 포트가 콜백으로 받은 repository 로 수행한다 — 파일 안에 save 호출이 없어도
`work(unit_of_work.repository)` escape 가 쓰기-사용으로 인정된다. helper 는 호출이 아니라
«호출 인자 참조 전달»로 도달한다.
"""
from __future__ import annotations

from collections.abc import Callable

from application.orders.application_layer.port.batch.batch_port import BatchPort
from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork


class ImportBatchUseCase:
    def __init__(self, execution_port: BatchPort,
                 unit_of_work_factory: Callable[[], OrdersUnitOfWork]) -> None:
        self._execution_port: BatchPort = execution_port
        self._unit_of_work_factory: Callable[[], OrdersUnitOfWork] = unit_of_work_factory

    def execute(self, bundle_path: str) -> None:
        self._execution_port.execute(bundle_path, run_batch=self._run_batch)

    def _run_batch(self, work: Callable) -> object:
        with self._unit_of_work_factory() as unit_of_work:
            return work(unit_of_work.repository)
