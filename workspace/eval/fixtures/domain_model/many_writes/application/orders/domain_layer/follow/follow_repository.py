from __future__ import annotations

from abc import ABC, abstractmethod

from application.orders.domain_layer.follow.follow import Follow


class FollowRepository(ABC):
    @abstractmethod
    def get(self, follower_id: str, followee_id: str) -> Follow: ...

    @abstractmethod
    def save(self, follow: Follow) -> None: ...

    @abstractmethod
    def save_with_version_guard(self, follow: Follow) -> bool: ...
