"""bad 행 3 — 같은 꼴 · 위치 인자 자리만 바뀜."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.follow.follow import Follow
from application.orders.domain_layer.follow.follow_repository import FollowRepository


class FollowBackByPositionUseCase:
    def __init__(self, follow_repository: FollowRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._follow_repository: FollowRepository = follow_repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, me: str, them: str) -> None:
        with self._unit_of_work:
            request: Follow = self._follow_repository.get(them, me)
            reverse: Follow = self._follow_repository.get(me, them)
            request.accept()
            reverse.accept()
            self._follow_repository.save(request)
            self._follow_repository.save(reverse)
