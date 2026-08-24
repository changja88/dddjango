from __future__ import annotations

from abc import ABC, abstractmethod


class WalletRepository(ABC):
    @abstractmethod
    def get(self, wallet_id: str) -> object: ...

    @abstractmethod
    def save(self, wallet: object) -> None: ...
