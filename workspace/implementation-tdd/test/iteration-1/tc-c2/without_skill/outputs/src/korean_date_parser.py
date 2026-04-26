"""
TDAID Step 3 (Green): 한국어 날짜 파서 구현
모든 테스트를 통과시키기 위한 최소 구현.

지원 형식:
  - 'YYYY년 MM월 DD일' (한국어)
  - 'YYYY/MM/DD' (슬래시)
  - 'YYYY-MM-DD' (하이픈)
"""

import re
from datetime import date

# 지원하는 날짜 형식의 정규식 패턴
_PATTERNS = [
    # 한국어 형식: 2026년 4월 5일
    re.compile(
        r"^(\d{1,4})년\s*(\d{1,2})월\s*(\d{1,2})일$"
    ),
    # 슬래시 형식: 2026/04/05
    re.compile(
        r"^(\d{4})/(\d{1,2})/(\d{1,2})$"
    ),
    # 하이픈 형식: 2026-04-05
    re.compile(
        r"^(\d{4})-(\d{1,2})-(\d{1,2})$"
    ),
]


def parse_korean_date(text: str) -> date:
    """한국어 날짜 문자열을 datetime.date 객체로 변환한다.

    Args:
        text: 파싱할 날짜 문자열.

    Returns:
        datetime.date 객체.

    Raises:
        TypeError: text가 문자열이 아닌 경우.
        ValueError: 인식할 수 없는 형식이거나 범위 밖의 날짜인 경우.
    """
    if not isinstance(text, str):
        raise TypeError(f"문자열이 필요합니다. 받은 타입: {type(text).__name__}")

    text = text.strip()
    if not text:
        raise ValueError("빈 문자열은 날짜로 변환할 수 없습니다.")

    for pattern in _PATTERNS:
        match = pattern.match(text)
        if match:
            year, month, day = (int(g) for g in match.groups())
            return _validate_and_build(year, month, day)

    raise ValueError(f"인식할 수 없는 날짜 형식입니다: '{text}'")


def _validate_and_build(year: int, month: int, day: int) -> date:
    """연, 월, 일 값을 검증하고 date 객체를 생성한다.

    Raises:
        ValueError: 범위 밖의 값이거나 존재하지 않는 날짜인 경우.
    """
    if year < 1:
        raise ValueError(f"연도는 1 이상이어야 합니다: {year}")
    if not (1 <= month <= 12):
        raise ValueError(f"월은 1~12 범위여야 합니다: {month}")
    if not (1 <= day <= 31):
        raise ValueError(f"일은 1~31 범위여야 합니다: {day}")

    try:
        return date(year, month, day)
    except ValueError:
        raise ValueError(
            f"존재하지 않는 날짜입니다: {year}년 {month}월 {day}일"
        )
