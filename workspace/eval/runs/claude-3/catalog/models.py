from django.db import models

from catalog.exceptions import InsufficientStock, StockUpdateConflict


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)
    # 낙관적 동시성 가드(OD-1 G1 확정 — 명세 §3.1·§3.3). default=0 으로 기존 행 즉시 충족.
    version = models.IntegerField(default=0)

    def deduct_stock(self, quantity: int) -> None:
        """재고를 quantity 만큼 차감한다(재고 소유자의 도메인 동작 — 명세 OD-1·§1.4).

        재고 충분성 판정(stock >= quantity)을 이 동작이 소유한다 — 판정을
        ordering 인프라 SQL 에 복제하지 않는다(명세 §1.4·§3.3 Rule ownership).
        차감은 version CAS 조건부 원자 UPDATE 로 수행한다: WHERE version=<읽은 version>
        은 경합 가드일 뿐이며, 충분성 판정은 아래 파이썬 조건이 내린다.

        - 재고 부족: InsufficientStock (영구 거절 — 명세 §1.3 → 409).
        - CAS 0행(경합): StockUpdateConflict (일시 경합, 재시도 트리거 — 명세 §3.3).
        """
        if self.stock < quantity:
            raise InsufficientStock(
                f"재고 부족: 가용 {self.stock}, 요청 {quantity}"
            )

        updated = Product.objects.filter(
            pk=self.pk,
            version=self.version,
        ).update(
            stock=models.F("stock") - quantity,
            version=models.F("version") + 1,
        )

        if updated == 0:
            # 다른 트랜잭션이 version 을 올림 — 재고 부족이 아니라 경합 신호.
            raise StockUpdateConflict(
                f"재고 차감 경합: product {self.pk}, version {self.version}"
            )

        # 인스턴스 상태를 차감 결과로 동기화한다.
        self.stock -= quantity
        self.version += 1
