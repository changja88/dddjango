"""ok 같은 관계를 키워드 차례만 바꿔 다시 읽음."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.follow.follow import Follow
from application.orders.domain_layer.follow.follow_repository import FollowRepository


class FollowRereadKeywordOrderUseCase:
    def __init__(self, follow_repository: FollowRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._follow_repository: FollowRepository = follow_repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, me: str, them: str) -> None:
        with self._unit_of_work:
            follow: Follow = self._follow_repository.get(follower_id=me, followee_id=them)
            follow.accept()
            self._follow_repository.save(follow)
            again: Follow = self._follow_repository.get(followee_id=them, follower_id=me)
            again.accept()
            self._follow_repository.save(again)
