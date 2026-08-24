"""#543 부칙(2026-08-25) — 저널 애그리거트 관용구(전건 충족 → 발화 해제 · kkebi 판형).

이벤트가 곧 도메인 실체: 실체 저장소(`events`)와 발행 대기 큐(`_pending_entries`)가 분리된
이중 구조 + pending 조회 property(tuple 사본) + 실소거 창구.
"""
from __future__ import annotations


class EventJournal:
    def __init__(self, journal_id: str) -> None:
        self.journal_id: str = journal_id
        self.events: list = []
        self._pending_entries: list = []

    def append_entry(self, entry: object) -> None:
        self.events.append(entry)
        self._pending_entries.append(entry)
        self._ensure_valid()

    @property
    def pending_entries(self) -> tuple:
        return tuple(self._pending_entries)

    def mark_entries_persisted(self) -> None:
        self._pending_entries.clear()

    def _ensure_valid(self) -> None:
        return None
