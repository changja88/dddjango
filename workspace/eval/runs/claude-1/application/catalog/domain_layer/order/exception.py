"""Order 측 도메인 예외."""


class ProductNotFound(Exception):
    """주문이 참조하는 Product가 존재하지 않을 때 발생 — 응용이 404로 번역."""

    def __init__(self, product_id: int) -> None:
        self.product_id = product_id
        super().__init__(f"Product {product_id} not found.")
