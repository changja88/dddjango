from __future__ import annotations

from application.orders.domain_layer.vault.event.vault_moved import VaultMoved


class Vault:
    def __init__(self, vault_id: str) -> None:
        self.vault_id: str = vault_id
        self._events: list = []

    def move(self) -> None:
        self._events.append(VaultMoved())

    def pull_events(self) -> list:
        drained: list = list(self._events)
        self._events.clear()
        return drained
