from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CasedModuleAmount:
    """통과 꼴이지만 옆의 대문자 폴더가 대소문자를 완화하는 환경에서 import 를 가로챈다(F2 — 직접 모듈 파일이 아니다)."""

    value: int
