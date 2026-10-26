from __future__ import annotations

from dataclasses import dataclass

from .currency import Currency


@dataclass(frozen=True)
class CurrencySymbol:
    currency: Currency
    mark: str

    def __post_init__(self) -> None:
        if not self.mark:
            raise ValueError("통화 기호")
