MAX_RETRIES: int = 3


class PlaceOrderUseCase:
    _timeout: float

    def __init__(self, repository: object) -> None:
        self._repository: object = repository
        self._timeout = 5.0

    def execute(self, command: object) -> object:
        total: int = 0
        for _ in range(MAX_RETRIES):
            total += 1
        return command
