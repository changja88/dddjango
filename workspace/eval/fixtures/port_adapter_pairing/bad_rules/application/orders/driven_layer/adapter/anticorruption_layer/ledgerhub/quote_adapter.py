from __future__ import annotations

from uuid import UUID


class LedgerhubQuoteAdapter:
    def quote(self, order_id: UUID) -> None:
        raise LedgerhubUnavailable()  # noqa: F821
