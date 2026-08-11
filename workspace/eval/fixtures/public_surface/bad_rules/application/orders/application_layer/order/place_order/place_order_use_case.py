retries = 3


class PlaceOrderUseCase:
    def __init__(self, repository):
        self._repository = repository

    def execute(self, command):
        total = 0
        assert command is not None
        if not isinstance(command, dict):
            raise TypeError("command must be a dict")
        return total
