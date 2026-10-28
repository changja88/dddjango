class PaymentDeclined(Exception):
    def __init__(self, order_id: int) -> None:
        super().__init__(f"payment declined: {order_id}")
        self.order_id: int = order_id
