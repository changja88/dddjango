"""한국어 날짜 파서 테스트 -- TDAID Red 단계에서 작성."""

from datetime import date

import pytest

from korean_date_parser import parse_korean_date


class TestParseKoreanDateFormat:
    """'YYYY년 M월 D일' 형식 파싱 테스트."""

    def test_parse_korean_date__standard__returns_date(self):
        assert parse_korean_date("2026년 4월 5일") == date(2026, 4, 5)

    def test_parse_korean_date__december__returns_date(self):
        assert parse_korean_date("2026년 12월 25일") == date(2026, 12, 25)

    def test_parse_korean_date__single_digit_month_day__returns_date(self):
        assert parse_korean_date("2026년 1월 1일") == date(2026, 1, 1)

    def test_parse_korean_date__padded_digits__returns_date(self):
        assert parse_korean_date("2026년 04월 05일") == date(2026, 4, 5)


class TestParseSlashFormat:
    """'YYYY/MM/DD' 형식 파싱 테스트."""

    def test_parse_slash__standard__returns_date(self):
        assert parse_korean_date("2026/04/05") == date(2026, 4, 5)

    def test_parse_slash__single_digit__returns_date(self):
        assert parse_korean_date("2026/1/1") == date(2026, 1, 1)


class TestParseDashFormat:
    """'YYYY-MM-DD' 형식 파싱 테스트."""

    def test_parse_dash__standard__returns_date(self):
        assert parse_korean_date("2026-04-05") == date(2026, 4, 5)

    def test_parse_dash__single_digit__returns_date(self):
        assert parse_korean_date("2026-1-1") == date(2026, 1, 1)


class TestInvalidInput:
    """잘못된 입력에 ValueError를 발생시키는 테스트."""

    def test_parse__empty_string__raises_value_error(self):
        with pytest.raises(ValueError):
            parse_korean_date("")

    def test_parse__random_text__raises_value_error(self):
        with pytest.raises(ValueError):
            parse_korean_date("잘못된 날짜")

    def test_parse__none_input__raises_value_error(self):
        with pytest.raises((ValueError, TypeError)):
            parse_korean_date(None)


class TestOutOfRangeInput:
    """범위 밖 날짜 입력 거부 테스트."""

    def test_parse__month_13__raises_value_error(self):
        with pytest.raises(ValueError):
            parse_korean_date("2026년 13월 1일")

    def test_parse__day_32__raises_value_error(self):
        with pytest.raises(ValueError):
            parse_korean_date("2026년 1월 32일")

    def test_parse__month_0__raises_value_error(self):
        with pytest.raises(ValueError):
            parse_korean_date("2026년 0월 1일")

    def test_parse__day_0__raises_value_error(self):
        with pytest.raises(ValueError):
            parse_korean_date("2026년 1월 0일")

    def test_parse__feb_30__raises_value_error(self):
        with pytest.raises(ValueError):
            parse_korean_date("2026-02-30")

    def test_parse__slash_month_13__raises_value_error(self):
        with pytest.raises(ValueError):
            parse_korean_date("2026/13/01")

    def test_parse__dash_day_32__raises_value_error(self):
        with pytest.raises(ValueError):
            parse_korean_date("2026-01-32")
