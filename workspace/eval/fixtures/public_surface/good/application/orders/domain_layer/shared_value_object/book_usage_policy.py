from enum import StrEnum as _StrEnum


class BookUsagePolicy(_StrEnum):
    """별칭으로 들여온 선언적 base — enum 멤버는 «문법이 없는 자리»라 주석을 달지 않는다(R-3154)."""

    SINGLE = "single"
    SOURCE_AND_COMMENTARY = "source_and_commentary"
