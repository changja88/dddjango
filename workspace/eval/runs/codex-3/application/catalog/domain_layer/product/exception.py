class ProductError(Exception):
    pass


class ProductNotFound(ProductError):
    pass


class InsufficientStock(ProductError):
    pass
