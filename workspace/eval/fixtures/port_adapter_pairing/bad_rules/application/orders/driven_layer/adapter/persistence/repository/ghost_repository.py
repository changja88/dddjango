from __future__ import annotations

from application.orders.domain_layer.ghost.ghost_repository import GhostRepository


class DjangoGhostRepository(GhostRepository):
    def get(self, ghost_id: str) -> object:
        return None

    def save(self, ghost: object) -> None:
        return None
