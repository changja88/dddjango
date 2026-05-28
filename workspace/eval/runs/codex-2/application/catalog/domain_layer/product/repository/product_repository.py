from typing import Protocol


class ProductRepository(Protocol):
    def reserve(self, product_id: int, quantity: int) -> tuple[int, int, int]:
        ...

