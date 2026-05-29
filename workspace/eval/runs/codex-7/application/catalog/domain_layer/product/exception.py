class ProductDomainError(Exception):
    pass


class InvalidReservationQuantity(ProductDomainError):
    def __init__(self, quantity: object) -> None:
        self.quantity = quantity
        super().__init__("Reservation quantity must be a positive integer.")


class InsufficientStock(ProductDomainError):
    def __init__(
        self, product_id: int, requested_quantity: int, available_stock: int
    ) -> None:
        self.product_id = product_id
        self.requested_quantity = requested_quantity
        self.available_stock = available_stock
        super().__init__(
            f"Product {product_id} has insufficient stock for the requested quantity."
        )
