from __future__ import annotations

from abc import ABC, abstractmethod

from application.orders.domain_layer.event_ledger.event_ledger import EventLedger


class EventLedgerRepository(ABC):
    @abstractmethod
    def get(self, event_ledger_id: str) -> EventLedger: ...

    @abstractmethod
    def save(self, event_ledger: EventLedger) -> None: ...
