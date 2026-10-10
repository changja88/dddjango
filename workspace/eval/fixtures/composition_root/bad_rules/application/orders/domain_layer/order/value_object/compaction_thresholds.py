from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class CompactionThresholds:
    """압축 시작과 강제 임계값의 유효한 조합이다(통과 모듈 — 생성식 반례의 짝)."""

    trigger: int
    force: int

    @classmethod
    def create(cls, *, trigger: int, force: int) -> CompactionThresholds:
        if trigger <= 0 or trigger >= force:
            raise ValueError("trigger 는 0 보다 크고 force 보다 작다")
        return cls(trigger=trigger, force=force)
