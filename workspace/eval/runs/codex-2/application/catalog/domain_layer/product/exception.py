class ProductError(Exception):
    pass


class InvalidReserveQuantity(ProductError):
    def __init__(self, quantity: int) -> None:
        self.quantity = quantity
        super().__init__("Reserve quantity must be at least 1.")


class ProductNotFound(ProductError):
    def __init__(self, product_id: int) -> None:
        self.product_id = product_id
        super().__init__("Product was not found.")


class InsufficientStock(ProductError):
    def __init__(self, *, product_id: int, requested_quantity: int, available_stock: int) -> None:
        self.product_id = product_id
        self.requested_quantity = requested_quantity
        self.available_stock = available_stock
        super().__init__("Requested quantity exceeds available stock.")


class DatabaseBusy(ProductError):
    pass

