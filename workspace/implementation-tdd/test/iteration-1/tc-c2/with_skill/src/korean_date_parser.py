"""한국어 날짜 파서 -- TDAID Green 단계에서 AI가 구현."""

import re
from datetime import date

_KOREAN_PATTERN = re.compile(
    r"^(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일$"
)
_SLASH_PATTERN = re.compile(
    r"^(\d{4})/(\d{1,2})/(\d{1,2})$"
)
_DASH_PATTERN = re.compile(
    r"^(\d{4})-(\d{1,2})-(\d{1,2})$"
)


def parse_korean_date(text: str) -> date:
    """한국어 날짜 문자열을 datetime.date로 변환한다.

    지원 형식:
        - 'YYYY년 M월 D일'
        - 'YYYY/MM/DD'
        - 'YYYY-MM-DD'

    Args:
        text: 날짜 문자열.

    Returns:
        파싱된 datetime.date 객체.

    Raises:
        ValueError: 인식할 수 없는 형식이거나 범위 밖 날짜.
        TypeError: text가 문자열이 아닌 경우.
    """
    if not isinstance(text, str):
        raise TypeError(f"문자열이 필요합니다: {type(text).__name__}")

    text = text.strip()
    if not text:
        raise ValueError("빈 문자열은 날짜로 변환할 수 없습니다")

    year, month, day = _extract_components(text)
    return _build_date(year, month, day)


def _extract_components(text: str) -> tuple[int, int, int]:
    for pattern in (_KOREAN_PATTERN, _SLASH_PATTERN, _DASH_PATTERN):
        match = pattern.match(text)
        if match:
            return int(match.group(1)), int(match.group(2)), int(match.group(3))
    raise ValueError(f"인식할 수 없는 날짜 형식입니다: '{text}'")


def _build_date(year: int, month: int, day: int) -> date:
    try:
        return date(year, month, day)
    except ValueError as e:
        raise ValueError(f"유효하지 않은 날짜입니다: {year}-{month}-{day} ({e})") from e
