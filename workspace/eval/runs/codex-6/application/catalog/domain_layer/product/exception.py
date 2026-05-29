class ProductDomainError(Exception):
    """Base class for product domain errors."""


class InvalidReservationQuantity(ProductDomainError):
    def __init__(self, quantity: int) -> None:
        super().__init__("Reservation quantity must be positive.")
        self.quantity = quantity


class InsufficientStock(ProductDomainError):
    def __init__(self, requested_quantity: int, available_stock: int) -> None:
        super().__init__("Requested quantity exceeds available stock.")
        self.requested_quantity = requested_quantity
        self.available_stock = available_stock
