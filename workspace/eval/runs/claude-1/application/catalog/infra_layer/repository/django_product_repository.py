"""DjangoProductRepository — ProductRepository 의 Django ORM 구현(인프라).

조건부 원자 UPDATE(WHERE stock >= qty)로 재고를 차감하고 rowcount를 반환한다(§4.3).
이 UPDATE의 stock - qty는 도메인이 내린 차감 결정의 영속 표현일 뿐, 인프라가 규칙을 발명하지 않는다.
"""
from typing import Optional

from django.db.models import F

from application.catalog.domain_layer.product.product import Product
from application.catalog.domain_layer.product.repository.product_repository import (
    ProductRepository,
)
from application.catalog.infra_layer.django_catalog.models.product_model import (
    ProductModel,
)


class DjangoProductRepository(ProductRepository):
    def find_by_id(self, product_id: int) -> Optional[Product]:
        try:
            row = ProductModel.objects.get(pk=product_id)
        except ProductModel.DoesNotExist:
            return None
        return Product(id=row.id, name=row.name, price=row.price, stock=row.stock)

    def deduct_stock(self, product_id: int, quantity: int) -> int:
        """WHERE stock >= quantity 가드의 단일 원자 UPDATE. 영향 행 수를 반환한다.

        1이면 차감 성공, 0이면 (상품 존재 & stock<qty) 재고 부족 — race 안전망.
        """
        return (
            ProductModel.objects.filter(pk=product_id, stock__gte=quantity)
            .update(stock=F("stock") - quantity)
        )
