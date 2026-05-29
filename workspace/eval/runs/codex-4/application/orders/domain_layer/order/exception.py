class OrderDomainError(Exception):
    pass


class InvalidQuantity(OrderDomainError):
    pass


class InsufficientStock(OrderDomainError):
    def __init__(self, *, available_stock: int, requested_quantity: int) -> None:
        self.available_stock = available_stock
        self.requested_quantity = requested_quantity
        super().__init__("insufficient stock")
