"""place_order 응용 서비스 (명세 §3.2·§3.3).

트랜잭션 경계를 소유하고 흐름을 조율한다 — 비즈니스 판정은 도메인에 위임한다
(빈혈 차단 — 명세 §3.2). 흐름: 단가 조회 → 도메인 Order.place 생성(수량 검증·
총액 계산) → ACL 포트로 재고 차감 위임(catalog 도메인 동작이 판정) → Order 영속화.
모두 하나의 atomic() 안 — 차감 거부면 트랜잭션 전체 롤백(주문 미생성).

경합 재시도 경계(명세 §3.3 Isolation/retry):
- 각 시도 = 독립 transaction.atomic() 블록, retry 루프는 트랜잭션 *밖*. 한 시도가
  경합으로 실패하면 atomic() 이 롤백되어 부분 변경이 다음 시도로 새지 않는다.
- version CAS 0행(경합)은 ACL 이 retryable 신호(StockDeductionConflict)로 올린다.
  잡으면 다음 시도에서 product 를 fresh 재조회(ACL 의 deduct/get_unit_price 가 매
  시도 새로 조회)해 도메인 동작(deduct_stock)부터 재실행한다 — stale version 재사용
  금지(명세 §3.3·§1.4).
- bounded retry 최대 3회. 상한 초과 시 StockContentionExhausted(→503, 409 와 의미
  분리 — 명세 §2.3 api M4). CAS 0행은 판정 대체물이 아니라 재시도 트리거다.
"""
from datetime import datetime, timezone
from typing import Callable

from django.db import transaction

from application.ordering.application_layer.place_order.dto.place_order_command import (
    PlaceOrderCommand,
)
from application.ordering.application_layer.place_order.dto.place_order_result import (
    PlaceOrderResult,
)
from application.ordering.domain_layer.order.exception import (
    StockContentionExhausted,
    StockDeductionConflict,
)
from application.ordering.domain_layer.order.order import Order
from application.ordering.domain_layer.order.port.product_stock_port import (
    ProductStockPort,
)
from application.ordering.domain_layer.order.repository.order_repository import (
    OrderRepository,
)
from application.ordering.domain_layer.order.value_object.quantity import Quantity

# 경합 재시도 상한(명세 §3.3 — bounded retry 최대 3회).
_MAX_ATTEMPTS = 3


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PlaceOrderApp:
    def __init__(
        self,
        *,
        stock_port: ProductStockPort,
        order_repository: OrderRepository,
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._stock_port = stock_port
        self._order_repository = order_repository
        self._clock = clock

    def execute(self, command: PlaceOrderCommand) -> PlaceOrderResult:
        """주문을 생성한다(트랜잭션 경계 소유, 경합 시 bounded retry)."""
        quantity = Quantity(command.quantity)

        # retry 루프는 트랜잭션 *밖*. 각 시도가 독립 atomic() 으로 격리된다(§3.3).
        for _attempt in range(_MAX_ATTEMPTS):
            try:
                persisted = self._attempt_place(command, quantity)
            except StockDeductionConflict:
                # CAS 0행 경합 — 이 시도의 atomic() 은 이미 롤백됨. 다음 시도에서
                # product 를 fresh 재조회해 도메인 동작부터 재실행한다(§3.3).
                continue
            return self._to_result(persisted)

        # 상한 소진 — 일시적 경합 소진(503), 영구 재고 부족(409)과 의미 분리.
        raise StockContentionExhausted(
            f"재고 차감 경합 재시도 상한({_MAX_ATTEMPTS}회) 초과: "
            f"product {command.product_id}"
        )

    def _attempt_place(
        self, command: PlaceOrderCommand, quantity: Quantity
    ) -> Order:
        """단일 차감 시도(독립 atomic 경계 — 명세 §3.2·§3.3).

        경합(StockDeductionConflict)이면 atomic() 이 롤백되어 부분 변경이 남지 않는다.
        """
        with transaction.atomic():
            unit_price = self._stock_port.get_unit_price(command.product_id)
            order = Order.place(
                product_id=command.product_id,
                quantity=quantity,
                unit_price=unit_price,
                now=self._clock(),
            )
            self._stock_port.deduct(command.product_id, quantity.value)
            return self._order_repository.add(order)

    @staticmethod
    def _to_result(order: Order) -> PlaceOrderResult:
        assert order.id is not None  # 영속화 후 id 부여됨
        return PlaceOrderResult(
            order_id=order.id,
            product_id=order.product_id,
            quantity=order.quantity.value,
            unit_price=order.unit_price,
            total_price=order.total_price,
            status=order.status.value,
            created_at=order.created_at,
        )
