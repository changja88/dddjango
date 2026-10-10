"""언어 코드 값 객체 — pre-gate 스텁 픽스처(D17 소유 · #652)의 재료 함수 반환 타입(V1 ~ V4 허용 목록 꼴)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LanguageCode:
    value: str
