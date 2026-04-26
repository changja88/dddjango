# OrderService.place_order 테스트

## 분석

`OrderService.place_order`는 다음 동작을 수행한다:
1. 빈 항목 목록에 대한 입력 검증
2. 주문 생성 및 합계 계산
3. 100,000 초과 시 10% 할인 적용
4. 저장소에 주문 저장
5. 결제 게이트웨이를 통한 결제 처리
6. 결제 실패 시 상태를 `payment_failed`로 변경 후 `PaymentError` 발생
7. 결제 성공 시 상태를 `confirmed`로 변경

외부 의존성: `order_repo`(저장소), `payment_gateway`(결제 게이트웨이) -- 이 두 가지만 Mock 대상이다.

검증 우선순위에 따라 출력 기반(반환값) > 상태 기반(order 객체 상태) > 통신 기반(mock 호출 검증) 순서로 검증한다.

## 테스트 코드

```python
from dataclasses import dataclass, field
from unittest.mock import Mock, call, create_autospec

import pytest


# --- 프로덕션 코드에서 가져와야 할 타입들 (테스트를 위한 최소 정의) ---

@dataclass
class Order:
    user_id: int
    status: str = "pending"
    total: float = 0.0
    discount: float | None = None
    id: int = 1


class PaymentError(Exception):
    pass


@dataclass
class PaymentResult:
    success: bool
    error_message: str = ""


class OrderRepository:
    """주문 저장소 인터페이스."""

    def save(self, order: Order) -> None: ...


class PaymentGateway:
    """결제 게이트웨이 인터페이스."""

    def charge(self, order_id: int, amount: float) -> PaymentResult: ...


# --- 테스트 대상 ---

class OrderService:
    def __init__(self, order_repo: OrderRepository, payment_gateway: PaymentGateway) -> None:
        self.order_repo = order_repo
        self.payment_gateway = payment_gateway

    def place_order(self, user_id: int, items: list[dict], shipping_address: str) -> Order:
        if not items:
            raise ValueError("주문 항목이 비어있습니다")

        order = Order(user_id=user_id, status="pending")
        total = sum(item["price"] * item["quantity"] for item in items)

        if total > 100000:
            order.discount = total * 0.1

        order.total = total - (order.discount or 0)
        self.order_repo.save(order)

        payment_result = self.payment_gateway.charge(order.id, order.total)
        if not payment_result.success:
            order.status = "payment_failed"
            self.order_repo.save(order)
            raise PaymentError(payment_result.error_message)

        order.status = "confirmed"
        self.order_repo.save(order)
        return order


# --- 픽스처 ---

@pytest.fixture
def order_repo() -> Mock:
    return create_autospec(OrderRepository, instance=True)


@pytest.fixture
def payment_gateway() -> Mock:
    mock = create_autospec(PaymentGateway, instance=True)
    mock.charge.return_value = PaymentResult(success=True)
    return mock


@pytest.fixture
def service(order_repo: Mock, payment_gateway: Mock) -> OrderService:
    return OrderService(order_repo=order_repo, payment_gateway=payment_gateway)


# --- 입력 검증 테스트 ---

class TestPlaceOrderValidation:
    """place_order의 입력 검증 동작을 검증한다."""

    def test_빈_항목_목록이면_value_error를_발생시킨다(
        self, service: OrderService
    ) -> None:
        with pytest.raises(ValueError, match="주문 항목이 비어있습니다"):
            service.place_order(user_id=1, items=[], shipping_address="서울시")

    def test_빈_항목이면_저장소에_저장하지_않는다(
        self, service: OrderService, order_repo: Mock
    ) -> None:
        with pytest.raises(ValueError):
            service.place_order(user_id=1, items=[], shipping_address="서울시")

        order_repo.save.assert_not_called()


# --- 합계 계산 테스트 ---

class TestPlaceOrderTotalCalculation:
    """place_order의 합계 및 할인 계산 동작을 검증한다."""

    def test_단일_항목의_합계를_올바르게_계산한다(
        self, service: OrderService, payment_gateway: Mock
    ) -> None:
        items = [{"price": 10000, "quantity": 2}]

        order = service.place_order(
            user_id=1, items=items, shipping_address="서울시"
        )

        assert order.total == 20000

    def test_여러_항목의_합계를_올바르게_계산한다(
        self, service: OrderService, payment_gateway: Mock
    ) -> None:
        items = [
            {"price": 5000, "quantity": 3},
            {"price": 8000, "quantity": 1},
        ]

        order = service.place_order(
            user_id=1, items=items, shipping_address="서울시"
        )

        assert order.total == 23000

    def test_합계가_100000_이하이면_할인이_없다(
        self, service: OrderService
    ) -> None:
        items = [{"price": 100000, "quantity": 1}]

        order = service.place_order(
            user_id=1, items=items, shipping_address="서울시"
        )

        assert order.discount is None
        assert order.total == 100000

    def test_합계가_100000_초과이면_10퍼센트_할인을_적용한다(
        self, service: OrderService
    ) -> None:
        items = [{"price": 100001, "quantity": 1}]

        order = service.place_order(
            user_id=1, items=items, shipping_address="서울시"
        )

        assert order.discount == pytest.approx(100001 * 0.1)
        assert order.total == pytest.approx(100001 - 100001 * 0.1)

    def test_합계가_경계값_100001이면_할인이_적용된다(
        self, service: OrderService
    ) -> None:
        """경계값: 100000은 할인 없음, 100001부터 할인 적용."""
        items = [{"price": 50000.5, "quantity": 2}]

        order = service.place_order(
            user_id=1, items=items, shipping_address="서울시"
        )

        assert order.discount is not None
        assert order.discount > 0

    @pytest.mark.parametrize(
        "price, quantity, expected_total",
        [
            (200000, 1, 200000 - 200000 * 0.1),
            (50000, 3, 150000 - 150000 * 0.1),
            (100002, 1, 100002 - 100002 * 0.1),
        ],
        ids=[
            "200000원-할인적용",
            "150000원-할인적용",
            "경계값-바로위-할인적용",
        ],
    )
    def test_할인_적용_후_최종_합계가_올바르다(
        self,
        service: OrderService,
        price: float,
        quantity: int,
        expected_total: float,
    ) -> None:
        items = [{"price": price, "quantity": quantity}]

        order = service.place_order(
            user_id=1, items=items, shipping_address="서울시"
        )

        assert order.total == pytest.approx(expected_total)


# --- 결제 성공 테스트 ---

class TestPlaceOrderPaymentSuccess:
    """결제가 성공했을 때의 동작을 검증한다."""

    def test_결제_성공시_confirmed_상태의_주문을_반환한다(
        self, service: OrderService
    ) -> None:
        items = [{"price": 10000, "quantity": 1}]

        order = service.place_order(
            user_id=1, items=items, shipping_address="서울시"
        )

        assert order.status == "confirmed"
        assert order.user_id == 1

    def test_결제_게이트웨이에_올바른_금액으로_결제를_요청한다(
        self, service: OrderService, payment_gateway: Mock
    ) -> None:
        items = [{"price": 30000, "quantity": 2}]

        order = service.place_order(
            user_id=1, items=items, shipping_address="서울시"
        )

        payment_gateway.charge.assert_called_once_with(order.id, 60000)

    def test_저장소에_주문을_총_2번_저장한다(
        self, service: OrderService, order_repo: Mock
    ) -> None:
        """결제 전 1회(pending), 결제 성공 후 1회(confirmed) = 총 2회."""
        items = [{"price": 10000, "quantity": 1}]

        service.place_order(
            user_id=1, items=items, shipping_address="서울시"
        )

        assert order_repo.save.call_count == 2


# --- 결제 실패 테스트 ---

class TestPlaceOrderPaymentFailure:
    """결제가 실패했을 때의 동작을 검증한다."""

    @pytest.fixture
    def failed_payment_gateway(self, payment_gateway: Mock) -> Mock:
        payment_gateway.charge.return_value = PaymentResult(
            success=False, error_message="잔액 부족"
        )
        return payment_gateway

    @pytest.fixture
    def failed_service(
        self, order_repo: Mock, failed_payment_gateway: Mock
    ) -> OrderService:
        return OrderService(
            order_repo=order_repo, payment_gateway=failed_payment_gateway
        )

    def test_결제_실패시_payment_error를_발생시킨다(
        self, failed_service: OrderService
    ) -> None:
        items = [{"price": 10000, "quantity": 1}]

        with pytest.raises(PaymentError, match="잔액 부족"):
            failed_service.place_order(
                user_id=1, items=items, shipping_address="서울시"
            )

    def test_결제_실패시_주문_상태가_payment_failed이다(
        self, failed_service: OrderService, order_repo: Mock
    ) -> None:
        items = [{"price": 10000, "quantity": 1}]

        with pytest.raises(PaymentError):
            failed_service.place_order(
                user_id=1, items=items, shipping_address="서울시"
            )

        saved_order = order_repo.save.call_args_list[-1][0][0]
        assert saved_order.status == "payment_failed"

    def test_결제_실패시_저장소에_주문을_총_2번_저장한다(
        self, failed_service: OrderService, order_repo: Mock
    ) -> None:
        """결제 전 1회(pending), 결제 실패 후 1회(payment_failed) = 총 2회."""
        items = [{"price": 10000, "quantity": 1}]

        with pytest.raises(PaymentError):
            failed_service.place_order(
                user_id=1, items=items, shipping_address="서울시"
            )

        assert order_repo.save.call_count == 2


# --- 저장 순서 검증 테스트 ---

class TestPlaceOrderSaveSequence:
    """저장소 호출의 순서와 주문 상태 전이를 검증한다."""

    def test_성공시_pending에서_confirmed로_상태가_전이된다(
        self, service: OrderService, order_repo: Mock
    ) -> None:
        items = [{"price": 10000, "quantity": 1}]
        saved_statuses: list[str] = []
        order_repo.save.side_effect = lambda o: saved_statuses.append(o.status)

        service.place_order(
            user_id=1, items=items, shipping_address="서울시"
        )

        assert saved_statuses == ["pending", "confirmed"]

    def test_실패시_pending에서_payment_failed로_상태가_전이된다(
        self, order_repo: Mock, payment_gateway: Mock
    ) -> None:
        payment_gateway.charge.return_value = PaymentResult(
            success=False, error_message="카드 거부"
        )
        service = OrderService(
            order_repo=order_repo, payment_gateway=payment_gateway
        )
        items = [{"price": 10000, "quantity": 1}]
        saved_statuses: list[str] = []
        order_repo.save.side_effect = lambda o: saved_statuses.append(o.status)

        with pytest.raises(PaymentError):
            service.place_order(
                user_id=1, items=items, shipping_address="서울시"
            )

        assert saved_statuses == ["pending", "payment_failed"]
```

## 테스트 설계 근거

### 검증 방식 선택
- **출력 기반 검증**(우선순위 1): `order.total`, `order.discount`, `order.status` 등 반환된 주문 객체의 값을 직접 검증한다.
- **상태 기반 검증**(우선순위 2): 결제 실패 경로에서 `order_repo.save`에 전달된 마지막 주문의 상태를 검증한다.
- **통신 기반 검증**(우선순위 3): `payment_gateway.charge` 호출 인자, `order_repo.save` 호출 횟수 등 외부 의존성과의 상호작용을 검증한다.

### Mock 범위
- `order_repo`와 `payment_gateway`는 외부 의존성이므로 `create_autospec`으로 Mock한다. spec을 지정하여 존재하지 않는 메서드 호출을 방지한다.
- 핵심 비즈니스 로직(합계 계산, 할인 적용, 상태 전이)은 실제 객체로 실행한다.

### 경계값 테스트
- 할인 조건 `total > 100000`에 대해 100000(할인 없음)과 100001(할인 적용) 경계값을 모두 검증한다. 이는 비교 연산자 변이(`>` vs `>=`)를 잡기 위한 것이다.

### 테스트 구조
- 클래스로 관련 동작을 그룹화한다: 입력 검증, 합계 계산, 결제 성공, 결제 실패, 저장 순서.
- 각 테스트는 하나의 동작만 검증하며, AAA(Arrange-Act-Assert) 패턴을 따른다.
- `parametrize`로 다양한 할인 금액 시나리오를 커버한다.

---
> **관련 스킬 참조:**
> - [TDD Red-Green-Refactor 방법론] -> **implementation-tdd** 스킬
> - [서비스 레이어 아키텍처 패턴] -> **implementation-django** 스킬
> - [Protocol 기반 의존성 주입] -> **implementation-python** 스킬
