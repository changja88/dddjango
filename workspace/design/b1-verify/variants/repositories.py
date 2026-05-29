"""리포지토리 — 영속화 경계. 핵심 관찰 대상: '비즈니스 규칙이 여기 새어드는가?'

- Naive/Optimistic: 영속화는 순수 배관(version 가드는 *경합 감지*이지 비즈니스 규칙이 아니다).
- Conditional: `stock__gte`(=비즈니스 규칙)가 SQL에 들어가 'repository는 로직을 갖지 않는다'를 위반한다.
"""
from django.db.models import F

from . import domain
from .models import ProductConditional, ProductNaive, ProductOptimistic


class NaiveRepository:
    """ORM ↔ 도메인 매핑 + 무방비 저장(lost update에 취약)."""

    def get(self, product_id: int) -> domain.Product:
        row = ProductNaive.objects.get(id=product_id)
        return domain.Product(id=row.id, stock=row.stock)

    def save(self, product: domain.Product) -> int:
        # 가드 없이 덮어쓴다 — stale write가 앞선 write를 지운다.
        return ProductNaive.objects.filter(id=product.id).update(stock=product.stock)


class OptimisticRepository:
    """version 가드만 — 비즈니스 규칙 없음. rowcount=0이면 경합."""

    def get(self, product_id: int) -> domain.Product:
        row = ProductOptimistic.objects.get(id=product_id)
        return domain.Product(id=row.id, stock=row.stock, version=row.version)

    def save(self, product: domain.Product) -> int:
        # WHERE version=<읽은 값> — 그새 누가 바꿨으면 매칭 0건. 단일 UPDATE라 portable·원자적.
        return ProductOptimistic.objects.filter(
            id=product.id, version=product.version
        ).update(stock=product.stock, version=product.version + 1)


class ConditionalRepository:
    """조건부 원자 UPDATE — `stock__gte`가 비즈니스 규칙을 SQL에 복제한다(B1 유발원)."""

    def deduct_stock(self, product_id: int, quantity: int) -> int:
        # 'stock>=quantity' 판정이 여기(인프라) 있다 — 도메인 deduct()를 군더더기로 만든다.
        return ProductConditional.objects.filter(
            id=product_id, stock__gte=quantity
        ).update(stock=F("stock") - quantity)
