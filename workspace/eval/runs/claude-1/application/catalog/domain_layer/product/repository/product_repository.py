"""ProductRepository — Product 영속화 추상화(ABC).

도메인이 의존하는 안정적 역할(포트). 구현은 인프라(DjangoProductRepository)가 제공한다.
"""
from abc import ABC, abstractmethod
from typing import Optional

from application.catalog.domain_layer.product.product import Product


class ProductRepository(ABC):
    @abstractmethod
    def find_by_id(self, product_id: int) -> Optional[Product]:
        """PK로 Product를 조회한다. 없으면 None."""
        raise NotImplementedError

    @abstractmethod
    def deduct_stock(self, product_id: int, quantity: int) -> int:
        """조건부 원자 UPDATE(WHERE stock >= quantity)로 재고를 차감한다(§4.3).

        영향받은 rowcount를 반환한다 — 1이면 차감 성공, 0이면 재고 부족(race 흡수).
        """
        raise NotImplementedError
