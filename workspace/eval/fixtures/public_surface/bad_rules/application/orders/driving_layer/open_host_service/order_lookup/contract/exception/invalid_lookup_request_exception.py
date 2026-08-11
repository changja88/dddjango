class OrderLookupError(Exception):
    pass


class InvalidLookupRequestException(OrderLookupError):
    def __init__(self, code: str) -> None:
        self.code: str = code
        super().__init__(code)
