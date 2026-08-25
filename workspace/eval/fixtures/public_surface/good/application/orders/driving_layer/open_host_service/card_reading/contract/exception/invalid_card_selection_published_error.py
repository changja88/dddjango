from .card_reading_published_error import CardReadingPublishedError


class InvalidCardSelectionPublishedError(CardReadingPublishedError):
    """semantic 실패 — 사용자 데이터 의존이라 타입으로 판정 불가(판정 ⑩ 인정 형상)."""

    def __init__(self, code: str) -> None:
        self.code: str = code
        super().__init__(code)
