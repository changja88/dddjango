from __future__ import annotations

from abc import ABC, abstractmethod


class VaultRepository(ABC):
    @abstractmethod
    def get(self, vault_id: str) -> object: ...

    @abstractmethod
    def save(self, vault: object) -> None: ...
