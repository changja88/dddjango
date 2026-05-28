"""DjangoProductRepository — 조건부 원자 UPDATE 차감과 rowcount 분류(설계 명세 section 3.2, 4).

동시성 정확성의 판정 권위가 이 구현에 있다: 단일 원자 UPDATE의 WHERE 가드로
검사와 쓰기를 DB에서 원자화하고, rowcount==0이면 동일 트랜잭션 재SELECT로
404(상품 없음)/409(재고 부족)를 분류한다.
"""

from __future__ import annotations

from django.db.models import F

from catalog.domain.exceptions import InsufficientStockError, ProductNotFoundError
from catalog.domain.product import Product as DomainProduct
from catalog.domain.product_repository import ProductRepository
from catalog.models import Product as ProductModel


class DjangoProductRepository(ProductRepository):
    def deduct_stock(self, product_id: int, quantity: int) -> DomainProduct:
        updated = (
            ProductModel.objects.filter(pk=product_id, stock__gte=quantity)
            .update(stock=F("stock") - quantity)
        )
        if updated == 0:
            self._classify_failure(product_id, quantity)

        row = ProductModel.objects.get(pk=product_id)
        return DomainProduct(
            id=row.id, name=row.name, price=row.price, stock=row.stock
        )

    def _classify_failure(self, product_id: int, quantity: int) -> None:
        """rowcount==0의 원인을 동일 트랜잭션 재SELECT로 분류한다(설계 명세 section 2.6).

        행이 있으면 재고 부족(409), 없으면 상품 없음(404).
        """
        row = ProductModel.objects.filter(pk=product_id).first()
        if row is None:
            raise ProductNotFoundError(product_id=product_id)
        raise InsufficientStockError(
            product_id=product_id, requested=quantity, available=row.stock
        )
