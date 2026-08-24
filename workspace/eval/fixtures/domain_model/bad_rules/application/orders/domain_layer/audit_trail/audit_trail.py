"""#543 부칙 경계(음성 2형 — red 유지).

AuditTrail: no-op mark 디코이 — 조회 property는 있지만 mark 가 아무것도 비우지 않는다(③ 탈락).
LogBook: 일반 관용구 흉내 — 저장소가 실체 이름 `_events` 그 자체라 이중 구조가 아니다(① 탈락 —
창구는 pull_events 하나).
"""
from __future__ import annotations


class AuditTrail:
    def __init__(self, trail_id: str) -> None:
        self.trail_id: str = trail_id
        self.events: list = []
        self._pending_entries: list = []

    @property
    def pending_entries(self) -> tuple:
        return tuple(self._pending_entries)

    def mark_entries_persisted(self) -> None:
        return None


class LogBook:
    def __init__(self, book_id: str) -> None:
        self.book_id: str = book_id
        self._events: list = []

    @property
    def pending_entries(self) -> tuple:
        return tuple(self._events)

    def mark_entries_persisted(self) -> None:
        self._events.clear()
