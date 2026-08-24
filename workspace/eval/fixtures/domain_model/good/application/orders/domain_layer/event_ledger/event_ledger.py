"""#543 부칙 경계 — 저널 구조 + `pull_events` 채택(kkebi 승인 R4-이후 형상 · 재발화 방지 pin)."""
from __future__ import annotations


class EventLedger:
    def __init__(self, ledger_id: str) -> None:
        self.ledger_id: str = ledger_id
        self.events: list = []
        self._pending_entries: list = []

    def append_entry(self, entry: object) -> None:
        self.events.append(entry)
        self._pending_entries.append(entry)
        self._ensure_valid()

    def pull_events(self) -> list:
        drained: list = list(self._pending_entries)
        self._pending_entries.clear()
        return drained

    def _ensure_valid(self) -> None:
        return None
