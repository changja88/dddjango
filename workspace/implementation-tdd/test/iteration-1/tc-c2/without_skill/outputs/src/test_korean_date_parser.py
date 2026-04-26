"""
TDAID Step 2 (Red): 한국어 날짜 파서 테스트
요구사항을 기반으로 실패하는 테스트를 먼저 작성한다.
"""

import pytest
from datetime import date

from korean_date_parser import parse_korean_date


# ── 1. 한국어 형식: 'YYYY년 MM월 DD일' ──

class TestKoreanFormat:
    def test_basic_korean_format(self):
        assert parse_korean_date("2026년 4월 5일") == date(2026, 4, 5)

    def test_korean_format_zero_padded(self):
        assert parse_korean_date("2026년 04월 05일") == date(2026, 4, 5)

    def test_korean_format_single_digit_month_day(self):
        assert parse_korean_date("2024년 1월 1일") == date(2024, 1, 1)

    def test_korean_format_december(self):
        assert parse_korean_date("2025년 12월 31일") == date(2025, 12, 31)


# ── 2. 슬래시 형식: 'YYYY/MM/DD' ──

class TestSlashFormat:
    def test_basic_slash_format(self):
        assert parse_korean_date("2026/04/05") == date(2026, 4, 5)

    def test_slash_format_no_padding(self):
        assert parse_korean_date("2026/4/5") == date(2026, 4, 5)

    def test_slash_format_end_of_year(self):
        assert parse_korean_date("2025/12/31") == date(2025, 12, 31)


# ── 3. 하이픈 형식: 'YYYY-MM-DD' ──

class TestHyphenFormat:
    def test_basic_hyphen_format(self):
        assert parse_korean_date("2026-04-05") == date(2026, 4, 5)

    def test_hyphen_format_no_padding(self):
        assert parse_korean_date("2026-4-5") == date(2026, 4, 5)

    def test_hyphen_format_leap_day(self):
        assert parse_korean_date("2024-02-29") == date(2024, 2, 29)


# ── 4. 잘못된 입력 → ValueError ──

class TestInvalidInput:
    def test_empty_string(self):
        with pytest.raises(ValueError):
            parse_korean_date("")

    def test_none_input(self):
        with pytest.raises((ValueError, TypeError)):
            parse_korean_date(None)

    def test_random_text(self):
        with pytest.raises(ValueError):
            parse_korean_date("안녕하세요")

    def test_partial_korean_format(self):
        with pytest.raises(ValueError):
            parse_korean_date("2026년 4월")

    def test_wrong_separator(self):
        with pytest.raises(ValueError):
            parse_korean_date("2026.04.05")

    def test_only_numbers(self):
        with pytest.raises(ValueError):
            parse_korean_date("20260405")


# ── 5. 범위 밖 입력 거부 ──

class TestOutOfRange:
    def test_month_13(self):
        with pytest.raises(ValueError):
            parse_korean_date("2026년 13월 1일")

    def test_month_zero(self):
        with pytest.raises(ValueError):
            parse_korean_date("2026년 0월 1일")

    def test_day_32(self):
        with pytest.raises(ValueError):
            parse_korean_date("2026년 4월 32일")

    def test_day_zero(self):
        with pytest.raises(ValueError):
            parse_korean_date("2026년 4월 0일")

    def test_feb_30(self):
        with pytest.raises(ValueError):
            parse_korean_date("2026-02-30")

    def test_non_leap_year_feb_29(self):
        with pytest.raises(ValueError):
            parse_korean_date("2025-02-29")

    def test_month_13_slash(self):
        with pytest.raises(ValueError):
            parse_korean_date("2026/13/01")

    def test_day_32_hyphen(self):
        with pytest.raises(ValueError):
            parse_korean_date("2026-04-32")

    def test_negative_year_korean(self):
        with pytest.raises(ValueError):
            parse_korean_date("-1년 4월 5일")
