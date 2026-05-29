"""애플리케이션 서비스(유스케이스) — 흐름 제어만. 비즈니스 규칙은 도메인에 위임한다.

여기가 V2(B1 불가능)의 관찰 지점이다:
- Optimistic/Naive: 프로덕션 경로가 domain.Product.deduct()를 *실제로 호출*한다 → 도메인이 권위.
- Conditional: 도메인을 우회하고 repo의 SQL 판정에 의존 → domain.deduct()는 죽은 코드(B1).
"""
from . import domain
from .repositories import (
    ConditionalRepository,
    NaiveRepository,
    OptimisticRepository,
)


class NaiveOrderService:
    def __init__(self) -> None:
        self.repo = NaiveRepository()

    def place_order(self, product_id: int, quantity: int) -> None:
        product = self.repo.get(product_id)
        product.deduct(quantity)  # 도메인 규칙 호출(메모리) — 단 stale snapshot 위에서.
        self.repo.save(product)


class OptimisticOrderService:
    def __init__(self, max_retries: int = 10) -> None:
        self.repo = OptimisticRepository()
        self.max_retries = max_retries

    def place_order(self, product_id: int, quantity: int) -> None:
        for _ in range(self.max_retries):
            product = self.repo.get(product_id)
            product.deduct(quantity)  # 권위 판정 — 매 시도 fresh 데이터로 재실행.
            rows = self.repo.save(product)
            if rows == 1:
                return
            # rows == 0: 그새 누가 version을 올림 → 재조회 후 처음부터 재시도.
        raise domain.ConcurrencyConflict("retry budget exhausted")


class ConditionalOrderService:
    def __init__(self) -> None:
        self.repo = ConditionalRepository()

    def place_order(self, product_id: int, quantity: int) -> None:
        # 도메인 deduct()를 부르지 않는다 — 판정을 SQL에 위임. domain.Product.deduct는 죽은 코드.
        rows = self.repo.deduct_stock(product_id, quantity)
        if rows == 0:
            raise domain.InsufficientStock("conditional update matched 0 rows")
