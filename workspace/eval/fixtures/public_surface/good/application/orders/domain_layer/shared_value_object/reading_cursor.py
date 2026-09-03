from dataclasses import dataclass as _dataclass


@_dataclass(frozen=True)
class ReadingCursor:
    """별칭으로 들여온 선언적 데코레이터 — plain `@dataclass` 와 같은 본문 면제를 받는다."""

    position: int

    DEFAULT_STEP = 1  # 클래스 상수 — 선언적 본문 관용(plain `@dataclass` 와 동일 취급)
