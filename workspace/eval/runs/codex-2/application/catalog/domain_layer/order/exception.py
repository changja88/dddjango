class OrderError(Exception):
    pass


class InvalidOrderQuantity(OrderError):
    def __init__(self, quantity: int) -> None:
        self.quantity = quantity
        super().__init__("Order quantity must be at least 1.")


class InvalidUnitPrice(OrderError):
    def __init__(self, unit_price: int) -> None:
        self.unit_price = unit_price
        super().__init__("Unit price must be non-negative.")

