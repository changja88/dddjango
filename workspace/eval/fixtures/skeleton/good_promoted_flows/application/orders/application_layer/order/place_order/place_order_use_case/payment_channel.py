class _PaymentChannel:
    def __init__(self, order_id: int) -> None:
        self._order_id: int = order_id

    def send(self, amount: int) -> bool:
        return amount > 0
