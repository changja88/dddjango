"""bad 행 3 — 맞팔 수락: 키워드 자리만 바뀐 두 조회(요청 · 역방향)를 함께 쓴다."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.follow.follow import Follow
from application.orders.domain_layer.follow.follow_repository import FollowRepository


class FollowBackByKeywordUseCase:
    def __init__(self, follow_repository: FollowRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._follow_repository: FollowRepository = follow_repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, me: str, them: str) -> None:
        with self._unit_of_work:
            request: Follow = self._follow_repository.get(follower_id=them, followee_id=me)
            reverse: Follow = self._follow_repository.get(follower_id=me, followee_id=them)
            request.accept()
            reverse.accept()
            self._follow_repository.save(request)
            self._follow_repository.save(reverse)
