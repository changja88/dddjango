"""Product 애그리거트 루트 (도메인).

재고 차감 불변식(I1·I2)의 권위(authority)를 소유한다(§1.4).
ORM(ProductModel)과 분리된 순수 도메인 객체 — DB 없이 단위 테스트 가능.
"""
from application.catalog.domain_layer.product.exception import InsufficientStock


class Product:
    """상품 — 재고(stock)를 보유하고 차감 규칙을 자기 경계에서 보호한다."""

    def __init__(self, id: int, name: str, price: int, stock: int) -> None:
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock

    def deduct(self, quantity: int) -> None:
        """재고를 quantity만큼 차감한다(권위 검사).

        I1: stock >= quantity 여야 차감 가능. 위반 시 InsufficientStock을 던지고
        상태를 바꾸지 않는다. 성공 시 in-memory stock을 stock - quantity로 줄인다(I2 보장).
        """
        if self.stock < quantity:
            raise InsufficientStock(
                available_stock=self.stock, requested_quantity=quantity
            )
        self.stock = self.stock - quantity
