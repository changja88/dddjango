class MalformedLookupPayloadError(Exception):
    """contract 팩토리가 raise 하는 형식 검증 — 판정 ⑩ 위반 형상."""

    def __init__(self, code: str) -> None:
        self.code: str = code
        super().__init__(code)
