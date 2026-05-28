"""카탈로그 BC 도메인 예외.

설계 명세 section 1.1 유비쿼터스 언어:
- InsufficientStockError: 재고 부족 -> 409 insufficient-stock
- ProductNotFoundError: 상품 없음 -> 404 product-not-found
"""


class CatalogDomainError(Exception):
    """카탈로그 도메인 예외의 최상위."""


class InsufficientStockError(CatalogDomainError):
    """요청 수량이 가용 재고를 초과해 차감을 거절한다(재고 변화 없음)."""

    def __init__(self, product_id: int, requested: int, available: int) -> None:
        self.product_id = product_id
        self.requested = requested
        self.available = available
        super().__init__(
            f"Requested quantity {requested} exceeds available stock {available}."
        )


class ProductNotFoundError(CatalogDomainError):
    """product_id에 해당하는 상품이 없거나 트랜잭션 중 사라졌다."""

    def __init__(self, product_id: int) -> None:
        self.product_id = product_id
        super().__init__(f"Product {product_id} does not exist.")
