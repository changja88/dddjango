from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ShadowedModuleAmount:
    """통과 꼴이지만 옆의 같은 이름 패키지가 import 를 가로챈다(F2 — 직접 모듈 파일이 아니다)."""

    value: int
