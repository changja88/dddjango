from __future__ import annotations

from abc import ABC, abstractmethod

from application.orders.domain_layer.event_journal.event_journal import EventJournal


class EventJournalRepository(ABC):
    @abstractmethod
    def get(self, event_journal_id: str) -> EventJournal: ...

    @abstractmethod
    def save(self, event_journal: EventJournal) -> None: ...
