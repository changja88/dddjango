from enum import StrEnum as _StrEnum


class BookUsagePolicy(_StrEnum):
    """근거 문헌을 묶어 읽는 방식."""

    SINGLE = "single"
    SOURCE_AND_COMMENTARY = "source_and_commentary"
    COMPARE = "compare"
