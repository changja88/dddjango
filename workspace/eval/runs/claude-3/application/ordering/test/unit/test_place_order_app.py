"""place_order 응용 서비스 흐름·재시도 경계 단위 테스트 (안쪽 루프).

근거: 설계 명세 §3.2(흐름·트랜잭션 경계)·§1.4(ACL 포트 협력)·§3.3(bounded retry
경계, Test criteria e).
fake 포트·리포지토리로 흐름(조회→도메인 생성→차감 위임→영속화)·결과 매핑·경합
재시도 경계를 검증한다. 실제 트랜잭션·DB·version CAS 는 통합/동시성 테스트가
덮으므로 여기서는 협력 구조와 재시도 결정만 결정론적으로 본다.

재시도 경계(§3.3): version CAS 0행(경합)이면 ACL 이 retryable 신호
(StockDeductionConflict)를 올리고, 응용 서비스가 재조회→도메인 동작 재실행으로
bounded retry(최대 3회) 한다. 상한 초과 시 StockContentionExhausted(→503).
"""
from datetime import datetime, timezone

from django.test import TestCase

from application.ordering.application_layer.place_order.command.place_order_app import (
    PlaceOrderApp,
)
from application.ordering.application_layer.place_order.dto.place_order_command import (
    PlaceOrderCommand,
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


class FakeProductStockPort(ProductStockPort):
    """단가를 돌려주고 차감 요청을 기록하는 fake 협력자."""

    def __init__(self, unit_price: int) -> None:
        self._unit_price = unit_price
        self.deduct_calls: list[tuple[int, int]] = []

    def get_unit_price(self, product_id: int) -> int:
        return self._unit_price

    def deduct(self, product_id: int, quantity: int) -> None:
        self.deduct_calls.append((product_id, quantity))


class ConflictingStockPort(ProductStockPort):
    """앞선 N회 차감 시도에 경합(StockDeductionConflict)을 내는 fake 협력자.

    응용 서비스의 bounded retry 경계를 결정론적으로 검증하기 위한 더블이다
    (실제 version 충돌 타이밍 없이 경합 신호만 강제).
    """

    def __init__(self, unit_price: int, conflicts_before_success: int) -> None:
        self._unit_price = unit_price
        self._remaining_conflicts = conflicts_before_success
        self.deduct_attempts = 0

    def get_unit_price(self, product_id: int) -> int:
        return self._unit_price

    def deduct(self, product_id: int, quantity: int) -> None:
        self.deduct_attempts += 1
        if self._remaining_conflicts > 0:
            self._remaining_conflicts -= 1
            raise StockDeductionConflict(
                f"경합: product {product_id}, attempt {self.deduct_attempts}"
            )


class FakeOrderRepository(OrderRepository):
    """식별자를 부여해 저장된 주문을 기록하는 fake 리포지토리."""

    def __init__(self) -> None:
        self.saved: list[Order] = []
        self._next_id = 1

    def add(self, order: Order) -> Order:
        order.assign_id(self._next_id)
        self._next_id += 1
        self.saved.append(order)
        return order


def _fixed_now() -> datetime:
    return datetime(2026, 5, 29, tzinfo=timezone.utc)


class PlaceOrderHappyPathTest(TestCase):
    """재고 충분 시 흐름·결과 매핑 (명세 §3.2·§5-1).

    협력자는 fake 이지만 응용 서비스가 소유한 트랜잭션 경계(atomic)는 실제 DB
    연결을 요구하므로 TestCase 로 둔다(흐름·매핑 검증, 실제 영속화는 fake).
    """

    def test_deducts_stock_and_persists_order(self) -> None:
        stock_port = FakeProductStockPort(unit_price=1000)
        repository = FakeOrderRepository()
        app = PlaceOrderApp(stock_port=stock_port, order_repository=repository, clock=_fixed_now)

        app.execute(PlaceOrderCommand(product_id=42, quantity=3))

        # 차감이 catalog 포트로 위임됨(oversell 차단의 핵심 협력)
        self.assertEqual(stock_port.deduct_calls, [(42, 3)])
        # 주문이 영속화됨
        self.assertEqual(len(repository.saved), 1)

    def test_result_carries_price_snapshot_and_status(self) -> None:
        stock_port = FakeProductStockPort(unit_price=1000)
        repository = FakeOrderRepository()
        app = PlaceOrderApp(stock_port=stock_port, order_repository=repository, clock=_fixed_now)

        result = app.execute(PlaceOrderCommand(product_id=42, quantity=3))

        self.assertEqual(result.order_id, 1)
        self.assertEqual(result.product_id, 42)
        self.assertEqual(result.quantity, 3)
        self.assertEqual(result.unit_price, 1000)
        self.assertEqual(result.total_price, 3000)
        self.assertEqual(result.status, "PLACED")
        self.assertEqual(result.created_at, _fixed_now())


class PlaceOrderRetryBoundaryTest(TestCase):
    """경합 재시도 경계 (명세 §3.3 Isolation/retry·criteria e).

    version CAS 0행 경합은 ACL 이 retryable 신호(StockDeductionConflict)로 올리고,
    응용 서비스가 재조회→도메인 동작 재실행으로 bounded retry(최대 3회) 한다.
    상한 초과 시 StockContentionExhausted(→503).
    """

    def test_retries_on_conflict_then_succeeds_within_bound(self) -> None:
        # 앞선 2회 경합 후 3번째 시도에서 성공 — 상한(3) 안이므로 주문 생성.
        stock_port = ConflictingStockPort(unit_price=1000, conflicts_before_success=2)
        repository = FakeOrderRepository()
        app = PlaceOrderApp(
            stock_port=stock_port, order_repository=repository, clock=_fixed_now
        )

        result = app.execute(PlaceOrderCommand(product_id=7, quantity=1))

        # 3회 시도(경합 2 + 성공 1)했고 주문이 결국 1건 생성됨.
        self.assertEqual(stock_port.deduct_attempts, 3)
        self.assertEqual(result.order_id, 1)
        self.assertEqual(len(repository.saved), 1)

    def test_raises_contention_exhausted_when_bound_exceeded(self) -> None:
        # 매 시도 경합 → 상한(3)을 소진해도 성공 못 함 → StockContentionExhausted.
        stock_port = ConflictingStockPort(
            unit_price=1000, conflicts_before_success=99
        )
        repository = FakeOrderRepository()
        app = PlaceOrderApp(
            stock_port=stock_port, order_repository=repository, clock=_fixed_now
        )

        with self.assertRaises(StockContentionExhausted):
            app.execute(PlaceOrderCommand(product_id=7, quantity=1))

        # 정확히 상한(3)만큼만 시도하고 멈춤 — 무한 재시도 금지.
        self.assertEqual(stock_port.deduct_attempts, 3)
        # 원자성: 어떤 시도도 주문을 영속화하지 않음(부분 변경 없음 — criteria e).
        self.assertEqual(len(repository.saved), 0)
