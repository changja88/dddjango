from __future__ import annotations

from abc import ABC, abstractmethod


class TokenVaultPort(ABC):
    @abstractmethod
    def issue_token(self) -> str: ...
