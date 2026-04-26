# 주문 할인 시스템: 빈혈 도메인 모델 -> 풍부한 도메인 모델 리팩토링

## 리팩토링 체크리스트

- [x] 빈혈 도메인 모델 -> 풍부한 도메인 모델로 비즈니스 로직 이동
- [x] 원시 타입 -> 값 객체로 추출
- [x] 서비스의 비즈니스 로직 -> 엔티티/값 객체의 메서드로 이동
- [x] 직접 참조 -> ID 참조로 변경
- [x] 큰 애그리거트 -> 작은 애그리거트로 분리 + 도메인 이벤트로 연결
- [x] 동기 호출 -> 도메인 이벤트 + 결과적 일관성으로 변경

---

## 1. 원시 타입 -> 값 객체로 추출

[Before]
```python
class Order:
    def __init__(self, id, customer_id, items, status, total, discount):
        self.id = id
        self.customer_id = customer_id
        self.items = items  # [{"product_id": "p1", "name": "A", "price": 10000, "qty": 2}]
        self.status = status  # "pending", "confirmed", "shipped", "cancelled"
        self.total = total
        self.discount = discount
```

[After]
```python
from __future__ import annotations
from dataclasses import dataclass, field, replace
from enum import Enum
from uuid import uuid4


# --- 값 객체 ---

@dataclass(frozen=True)
class Money:
    """금액 값 객체 -- 불변, 부작용 없는 연산"""
    amount: int
    currency: str = "KRW"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError(f"금액은 0 이상이어야 합니다: {self.amount}")

    def add(self, other: Money) -> Money:
        self._ensure_same_currency(other)
        return replace(self, amount=self.amount + other.amount)

    def subtract(self, other: Money) -> Money:
        self._ensure_same_currency(other)
        if self.amount - other.amount < 0:
            raise ValueError("결과 금액이 음수입니다")
        return replace(self, amount=self.amount - other.amount)

    def multiply(self, factor: int) -> Money:
        return replace(self, amount=self.amount * factor)

    def rate(self, percentage: float) -> Money:
        """비율 계산 -- 연산의 닫힘(Closure of Operations): Money -> Money"""
        return replace(self, amount=int(self.amount * percentage))

    def _ensure_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise ValueError(f"통화 불일치: {self.currency} != {other.currency}")

    @classmethod
    def zero(cls) -> Money:
        return cls(amount=0)


@dataclass(frozen=True)
class OrderLineItem:
    """주문 항목 값 객체 -- 불변, 자기 완결적"""
    product_id: str
    product_name: str
    price: Money
    quantity: int

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError(f"수량은 1 이상이어야 합니다: {self.quantity}")

    @property
    def amounts(self) -> Money:
        """항목 소계 -- 부작용 없는 함수"""
        return self.price.multiply(self.quantity)


class OrderStatus(Enum):
    """주문 상태 값 객체 -- 상태 전이 규칙을 캡슐화"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"

    @property
    def is_confirmable(self) -> bool:
        return self == OrderStatus.PENDING

    @property
    def is_cancellable(self) -> bool:
        return self not in (OrderStatus.SHIPPED, OrderStatus.CANCELLED)


class CustomerGrade(Enum):
    """고객 등급 값 객체 -- 등급별 할인율을 도메인 지식으로 캡슐화"""
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    VIP = "VIP"

    @property
    def discount_rate(self) -> float:
        rates = {
            CustomerGrade.BRONZE: 0.0,
            CustomerGrade.SILVER: 0.01,
            CustomerGrade.GOLD: 0.03,
            CustomerGrade.VIP: 0.05,
        }
        return rates[self]
```

[Reason] 값 객체(Value Object) + 부작용 없는 함수(Side-Effect-Free Functions) -- 원시 타입(`int`, `str`)은 도메인 의미를 표현하지 못하고 유효성 검증이 분산된다. `Money`는 불변이며 모든 연산이 새 객체를 반환하므로 부작용이 없다. `OrderStatus`와 `CustomerGrade`는 Enum으로 도메인 규칙(상태 전이 가능 여부, 등급별 할인율)을 값 객체 안에 캡슐화하여 유비쿼터스 언어를 코드에 반영한다. `OrderLineItem`은 dict 대신 불변 값 객체로 추출하여 소계 계산 로직을 자체적으로 수행한다.

---

## 2. 빈혈 도메인 모델 -> 풍부한 도메인 모델 (비즈니스 로직 이동)

[Before]
```python
class Order:
    def __init__(self, id, customer_id, items, status, total, discount):
        self.id = id
        self.customer_id = customer_id
        self.items = items
        self.status = status
        self.total = total
        self.discount = discount

class OrderService:
    def create_order(self, customer_id, items):
        total = sum(i["price"] * i["qty"] for i in items)
        order = Order(id=uuid4(), customer_id=customer_id, items=items,
                      status="pending", total=total, discount=0)
        return order

    def confirm_order(self, order):
        if order.status != "pending":
            raise ValueError("대기 상태만 확정 가능")
        if not order.items:
            raise ValueError("상품이 없습니다")
        order.status = "confirmed"

    def cancel_order(self, order):
        if order.status in ("shipped", "cancelled"):
            raise ValueError("취소 불가능한 상태")
        order.status = "cancelled"
```

[After]
```python
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class DomainEvent:
    """도메인 이벤트 기본 클래스"""
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class OrderConfirmedEvent(DomainEvent):
    """주문 확정 이벤트 -- 결과적 일관성을 위한 이벤트 발행"""
    order_id: str = ""
    customer_id: str = ""
    total_amount: int = 0


@dataclass(frozen=True)
class OrderCancelledEvent(DomainEvent):
    """주문 취소 이벤트"""
    order_id: str = ""
    customer_id: str = ""


@dataclass
class Order:
    """주문 애그리거트 루트

    - 모든 상태 변경은 Order의 메서드를 통해서만 수행한다
    - 비즈니스 규칙(불변식)이 애그리거트 안에 위치한다
    - 다른 애그리거트(Customer)는 ID로만 참조한다 (Vernon 규칙 3)
    - 도메인 이벤트를 수집하여 결과적 일관성을 지원한다 (Vernon 규칙 4)
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    customer_id: str = ""  # Customer 애그리거트를 ID로 참조
    _order_lines: List[OrderLineItem] = field(default_factory=list)
    _status: OrderStatus = field(default=OrderStatus.PENDING)
    _discount: Money = field(default_factory=Money.zero)
    _events: List[DomainEvent] = field(default_factory=list)

    def __post_init__(self) -> None:
        """생성 시점에 불변식을 강제한다"""
        self._verify_at_least_one_line()
        self._total: Money = self._calculate_total()

    # --- 불변식 검증 (진정한 불변식을 일관성 경계 안에서 보호) ---

    def _verify_at_least_one_line(self) -> None:
        if not self._order_lines:
            raise ValueError("최소 한 개의 상품이 필요합니다")

    def _calculate_total(self) -> Money:
        total = Money.zero()
        for line in self._order_lines:
            total = total.add(line.amounts)
        return total

    # --- 의도를 드러내는 인터페이스 (비즈니스 행위) ---

    def confirm(self) -> None:
        """주문 확정 -- 유비쿼터스 언어 반영 (updateStatus가 아닌 confirm)"""
        if not self._status.is_confirmable:
            raise ValueError(
                f"{self._status.value} 상태에서는 확정할 수 없습니다. "
                f"대기(pending) 상태만 확정 가능합니다."
            )
        self._status = OrderStatus.CONFIRMED
        self._raise_event(
            OrderConfirmedEvent(
                order_id=self.id,
                customer_id=self.customer_id,
                total_amount=self.payment_amount.amount,
            )
        )

    def cancel(self) -> None:
        """주문 취소 -- 유비쿼터스 언어 반영"""
        if not self._status.is_cancellable:
            raise ValueError(
                f"{self._status.value} 상태에서는 취소할 수 없습니다."
            )
        self._status = OrderStatus.CANCELLED
        self._raise_event(
            OrderCancelledEvent(
                order_id=self.id,
                customer_id=self.customer_id,
            )
        )

    def apply_discount(self, discount: Money) -> None:
        """할인 적용 -- 애그리거트가 도메인 서비스를 모른다 (Money 값만 받음)"""
        if discount.amount < 0:
            raise ValueError("할인 금액은 0 이상이어야 합니다")
        if discount.amount > self._total.amount:
            raise ValueError("할인 금액이 주문 총액을 초과할 수 없습니다")
        self._discount = discount

    # --- 조회 (부작용 없는 함수) ---

    @property
    def order_lines(self) -> List[OrderLineItem]:
        return list(self._order_lines)

    @property
    def status(self) -> OrderStatus:
        return self._status

    @property
    def total(self) -> Money:
        return self._total

    @property
    def discount(self) -> Money:
        return self._discount

    @property
    def payment_amount(self) -> Money:
        """최종 결제 금액 = 총액 - 할인"""
        return self._total.subtract(self._discount)

    # --- 도메인 이벤트 수집 ---

    def _raise_event(self, event: DomainEvent) -> None:
        self._events.append(event)

    def collect_domain_events(self) -> List[DomainEvent]:
        events = list(self._events)
        self._events.clear()
        return events
```

[Reason] 풍부한 도메인 모델(Rich Domain Model) + 의도를 드러내는 인터페이스(Intention-Revealing Interfaces) -- 빈혈 도메인 모델에서는 `Order`가 데이터만 보유하고 `OrderService`가 모든 비즈니스 로직을 수행했다. 이는 절차적 프로그래밍과 동일하며, Millett가 "가장 흔한 DDD 실패 사례"로 지적한 안티패턴이다. 리팩토링 후 `Order` 애그리거트가 상태 전이 규칙(`confirm`, `cancel`), 불변식 검증(`_verify_at_least_one_line`), 금액 계산(`_calculate_total`, `payment_amount`)을 직접 수행한다. 메서드 이름은 `updateStatus`가 아닌 `confirm()`, `cancel()`로 비즈니스 의도를 드러낸다.

---

## 3. 서비스의 비즈니스 로직 -> 도메인 서비스 + 응용 서비스 분리

[Before]
```python
class OrderService:
    def apply_discount(self, order, coupon_code, customer_grade):
        coupon = self.coupon_repo.find(coupon_code)
        if coupon and coupon.is_valid():
            order.discount += coupon.amount
        if customer_grade == "VIP":
            order.discount += int(order.total * 0.05)
        elif customer_grade == "GOLD":
            order.discount += int(order.total * 0.03)
        order.total = order.total - order.discount
```

[After]
```python
@dataclass(frozen=True)
class Coupon:
    """쿠폰 값 객체"""
    code: str
    discount_amount: Money
    is_valid: bool


class DiscountCalculationService:
    """할인 계산 도메인 서비스

    - 상태가 없다 (stateless)
    - 여러 애그리거트(주문, 쿠폰, 회원)의 데이터를 사용하여 계산
    - 한 애그리거트에 넣기 애매한 로직을 명시적으로 표현
    - 애그리거트가 이 서비스를 모른다 (결과 Money만 전달받음)
    """

    def calculate_discount(
        self,
        order_total: Money,
        coupons: List[Coupon],
        customer_grade: CustomerGrade,
    ) -> Money:
        coupon_discount = self._calculate_coupon_discount(coupons)
        grade_discount = self._calculate_grade_discount(order_total, customer_grade)
        total_discount = coupon_discount.add(grade_discount)

        # 할인 총액이 주문 총액을 초과하지 않도록 보호
        if total_discount.amount > order_total.amount:
            return order_total
        return total_discount

    def _calculate_coupon_discount(self, coupons: List[Coupon]) -> Money:
        discount = Money.zero()
        for coupon in coupons:
            if coupon.is_valid:
                discount = discount.add(coupon.discount_amount)
        return discount

    def _calculate_grade_discount(
        self, order_total: Money, grade: CustomerGrade
    ) -> Money:
        return order_total.rate(grade.discount_rate)


class OrderApplicationService:
    """주문 응용 서비스

    - 비즈니스 로직을 직접 구현하지 않는다
    - 도메인 객체에 위임한다
    - 트랜잭션과 조율만 담당한다
    """

    def __init__(
        self,
        order_repository: "OrderRepository",
        coupon_repository: "CouponRepository",
        discount_service: DiscountCalculationService,
    ):
        self._order_repo = order_repository
        self._coupon_repo = coupon_repository
        self._discount_service = discount_service

    def create_order(
        self, customer_id: str, items: List[OrderLineItem]
    ) -> str:
        """주문 생성 -- 불변식 검증은 Order 애그리거트가 수행"""
        order = Order(
            customer_id=customer_id,
            _order_lines=items,
        )
        self._order_repo.save(order)
        return order.id

    def apply_discount(
        self,
        order_id: str,
        coupon_codes: List[str],
        customer_grade: CustomerGrade,
    ) -> None:
        """할인 적용 -- 도메인 서비스로 계산하고 결과를 애그리거트에 전달"""
        order = self._order_repo.find_by_id(order_id)
        if order is None:
            raise ValueError("주문을 찾을 수 없습니다")

        # 쿠폰 조회 (응용 서비스의 조율 책임)
        coupons = [
            self._coupon_repo.find(code)
            for code in coupon_codes
            if self._coupon_repo.find(code) is not None
        ]

        # 도메인 서비스로 할인 계산
        discount = self._discount_service.calculate_discount(
            order.total, coupons, customer_grade
        )

        # 애그리거트에 할인 적용 (Money 값만 전달, 서비스를 모름)
        order.apply_discount(discount)
        self._order_repo.save(order)

    def confirm_order(self, order_id: str) -> None:
        """주문 확정 -- 도메인 로직은 Order에 위임"""
        order = self._order_repo.find_by_id(order_id)
        if order is None:
            raise ValueError("주문을 찾을 수 없습니다")
        order.confirm()  # 비즈니스 규칙은 애그리거트 안에
        self._order_repo.save(order)

    def cancel_order(self, order_id: str) -> None:
        """주문 취소 -- 도메인 로직은 Order에 위임"""
        order = self._order_repo.find_by_id(order_id)
        if order is None:
            raise ValueError("주문을 찾을 수 없습니다")
        order.cancel()  # 비즈니스 규칙은 애그리거트 안에
        self._order_repo.save(order)
```

[Reason] 도메인 서비스 + 응용 서비스 분리 -- 기존 `OrderService.apply_discount`는 쿠폰 조회(인프라 관심사), 할인 계산(도메인 로직), 주문 상태 직접 변경(애그리거트 침범)을 하나의 메서드에 혼합하고 있었다. 할인 계산은 여러 애그리거트(주문, 쿠폰, 회원)에 걸친 도메인 로직이므로 `DiscountCalculationService` 도메인 서비스로 분리한다. 응용 서비스(`OrderApplicationService`)는 리포지토리 조회, 도메인 서비스 호출, 애그리거트 메서드 호출의 조율만 담당한다. 애그리거트는 계산된 `Money` 값만 받으므로 외부 의존성이 없다.

---

## 전체 코드 (통합)

```python
from __future__ import annotations
from dataclasses import dataclass, field, replace
from datetime import datetime
from enum import Enum
from typing import List
from uuid import uuid4


# ============================================================
# 값 객체 (Value Objects)
# ============================================================

@dataclass(frozen=True)
class Money:
    """금액 값 객체 -- 불변, 부작용 없는 연산, 연산의 닫힘"""
    amount: int
    currency: str = "KRW"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError(f"금액은 0 이상이어야 합니다: {self.amount}")

    def add(self, other: Money) -> Money:
        self._ensure_same_currency(other)
        return replace(self, amount=self.amount + other.amount)

    def subtract(self, other: Money) -> Money:
        self._ensure_same_currency(other)
        if self.amount - other.amount < 0:
            raise ValueError("결과 금액이 음수입니다")
        return replace(self, amount=self.amount - other.amount)

    def multiply(self, factor: int) -> Money:
        return replace(self, amount=self.amount * factor)

    def rate(self, percentage: float) -> Money:
        return replace(self, amount=int(self.amount * percentage))

    def _ensure_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise ValueError(f"통화 불일치: {self.currency} != {other.currency}")

    @classmethod
    def zero(cls) -> Money:
        return cls(amount=0)


@dataclass(frozen=True)
class OrderLineItem:
    """주문 항목 값 객체"""
    product_id: str
    product_name: str
    price: Money
    quantity: int

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError(f"수량은 1 이상이어야 합니다: {self.quantity}")

    @property
    def amounts(self) -> Money:
        return self.price.multiply(self.quantity)


class OrderStatus(Enum):
    """주문 상태 -- 상태 전이 규칙을 캡슐화"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"

    @property
    def is_confirmable(self) -> bool:
        return self == OrderStatus.PENDING

    @property
    def is_cancellable(self) -> bool:
        return self not in (OrderStatus.SHIPPED, OrderStatus.CANCELLED)


class CustomerGrade(Enum):
    """고객 등급 -- 등급별 할인율을 도메인 지식으로 캡슐화"""
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    VIP = "VIP"

    @property
    def discount_rate(self) -> float:
        rates = {
            CustomerGrade.BRONZE: 0.0,
            CustomerGrade.SILVER: 0.01,
            CustomerGrade.GOLD: 0.03,
            CustomerGrade.VIP: 0.05,
        }
        return rates[self]


@dataclass(frozen=True)
class Coupon:
    """쿠폰 값 객체"""
    code: str
    discount_amount: Money
    is_valid: bool


# ============================================================
# 도메인 이벤트 (Domain Events)
# ============================================================

@dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class OrderConfirmedEvent(DomainEvent):
    order_id: str = ""
    customer_id: str = ""
    total_amount: int = 0


@dataclass(frozen=True)
class OrderCancelledEvent(DomainEvent):
    order_id: str = ""
    customer_id: str = ""


# ============================================================
# 애그리거트 (Aggregate Root)
# ============================================================

@dataclass
class Order:
    """주문 애그리거트 루트

    Vernon의 4가지 규칙 적용:
    1. 진정한 불변식(최소 1개 항목, 금액 >= 0)을 일관성 경계 안에서 보호
    2. 작은 애그리거트 -- 핵심 속성과 OrderLineItem만 포함
    3. Customer는 ID로만 참조 (customer_id)
    4. 도메인 이벤트로 결과적 일관성 지원
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    customer_id: str = ""
    _order_lines: List[OrderLineItem] = field(default_factory=list)
    _status: OrderStatus = field(default=OrderStatus.PENDING)
    _discount: Money = field(default_factory=Money.zero)
    _events: List[DomainEvent] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._verify_at_least_one_line()
        self._total: Money = self._calculate_total()

    # --- 불변식 ---

    def _verify_at_least_one_line(self) -> None:
        if not self._order_lines:
            raise ValueError("최소 한 개의 상품이 필요합니다")

    def _calculate_total(self) -> Money:
        total = Money.zero()
        for line in self._order_lines:
            total = total.add(line.amounts)
        return total

    # --- 비즈니스 행위 (의도를 드러내는 인터페이스) ---

    def confirm(self) -> None:
        if not self._status.is_confirmable:
            raise ValueError(
                f"{self._status.value} 상태에서는 확정할 수 없습니다. "
                f"대기(pending) 상태만 확정 가능합니다."
            )
        self._status = OrderStatus.CONFIRMED
        self._raise_event(
            OrderConfirmedEvent(
                order_id=self.id,
                customer_id=self.customer_id,
                total_amount=self.payment_amount.amount,
            )
        )

    def cancel(self) -> None:
        if not self._status.is_cancellable:
            raise ValueError(
                f"{self._status.value} 상태에서는 취소할 수 없습니다."
            )
        self._status = OrderStatus.CANCELLED
        self._raise_event(
            OrderCancelledEvent(
                order_id=self.id,
                customer_id=self.customer_id,
            )
        )

    def apply_discount(self, discount: Money) -> None:
        if discount.amount < 0:
            raise ValueError("할인 금액은 0 이상이어야 합니다")
        if discount.amount > self._total.amount:
            raise ValueError("할인 금액이 주문 총액을 초과할 수 없습니다")
        self._discount = discount

    # --- 조회 ---

    @property
    def order_lines(self) -> List[OrderLineItem]:
        return list(self._order_lines)

    @property
    def status(self) -> OrderStatus:
        return self._status

    @property
    def total(self) -> Money:
        return self._total

    @property
    def discount(self) -> Money:
        return self._discount

    @property
    def payment_amount(self) -> Money:
        return self._total.subtract(self._discount)

    # --- 도메인 이벤트 ---

    def _raise_event(self, event: DomainEvent) -> None:
        self._events.append(event)

    def collect_domain_events(self) -> List[DomainEvent]:
        events = list(self._events)
        self._events.clear()
        return events


# ============================================================
# 도메인 서비스 (Domain Service)
# ============================================================

class DiscountCalculationService:
    """할인 계산 도메인 서비스 -- stateless, 여러 애그리거트에 걸친 계산"""

    def calculate_discount(
        self,
        order_total: Money,
        coupons: List[Coupon],
        customer_grade: CustomerGrade,
    ) -> Money:
        coupon_discount = self._calculate_coupon_discount(coupons)
        grade_discount = self._calculate_grade_discount(order_total, customer_grade)
        total_discount = coupon_discount.add(grade_discount)

        if total_discount.amount > order_total.amount:
            return order_total
        return total_discount

    def _calculate_coupon_discount(self, coupons: List[Coupon]) -> Money:
        discount = Money.zero()
        for coupon in coupons:
            if coupon.is_valid:
                discount = discount.add(coupon.discount_amount)
        return discount

    def _calculate_grade_discount(
        self, order_total: Money, grade: CustomerGrade
    ) -> Money:
        return order_total.rate(grade.discount_rate)


# ============================================================
# 응용 서비스 (Application Service)
# ============================================================

class OrderApplicationService:
    """주문 응용 서비스 -- 비즈니스 로직 없이 조율만 담당"""

    def __init__(
        self,
        order_repository: "OrderRepository",
        coupon_repository: "CouponRepository",
        discount_service: DiscountCalculationService,
    ):
        self._order_repo = order_repository
        self._coupon_repo = coupon_repository
        self._discount_service = discount_service

    def create_order(
        self, customer_id: str, items: List[OrderLineItem]
    ) -> str:
        order = Order(customer_id=customer_id, _order_lines=items)
        self._order_repo.save(order)
        return order.id

    def apply_discount(
        self,
        order_id: str,
        coupon_codes: List[str],
        customer_grade: CustomerGrade,
    ) -> None:
        order = self._order_repo.find_by_id(order_id)
        if order is None:
            raise ValueError("주문을 찾을 수 없습니다")

        coupons = [
            self._coupon_repo.find(code)
            for code in coupon_codes
            if self._coupon_repo.find(code) is not None
        ]

        discount = self._discount_service.calculate_discount(
            order.total, coupons, customer_grade
        )
        order.apply_discount(discount)
        self._order_repo.save(order)

    def confirm_order(self, order_id: str) -> None:
        order = self._order_repo.find_by_id(order_id)
        if order is None:
            raise ValueError("주문을 찾을 수 없습니다")
        order.confirm()
        self._order_repo.save(order)

    def cancel_order(self, order_id: str) -> None:
        order = self._order_repo.find_by_id(order_id)
        if order is None:
            raise ValueError("주문을 찾을 수 없습니다")
        order.cancel()
        self._order_repo.save(order)
```

## 적용된 DDD 원칙 요약

| 원칙 | Before (문제) | After (개선) |
|------|--------------|-------------|
| 풍부한 도메인 모델 | `Order`는 데이터만 보유, 모든 로직이 `OrderService`에 분산 | `Order` 애그리거트가 상태 전이, 불변식 검증, 금액 계산을 직접 수행 |
| 값 객체 | `int`/`str`/`dict`로 금액, 상태, 등급, 항목을 표현 | `Money`, `OrderStatus`, `CustomerGrade`, `OrderLineItem`으로 도메인 개념을 타입으로 표현 |
| 의도를 드러내는 인터페이스 | `confirm_order(order)` -- 외부에서 상태를 직접 변경 | `order.confirm()` -- 비즈니스 의도를 드러내는 메서드 |
| 부작용 없는 함수 | `order.total = order.total - order.discount` -- 직접 변경 | `Money.subtract()` 등 모든 값 객체 연산이 새 객체를 반환 |
| 도메인 서비스 | 할인 계산이 쿠폰 조회와 혼합 | `DiscountCalculationService`가 순수 계산만 담당 (stateless) |
| 응용 서비스 | `OrderService`가 비즈니스 로직과 조율을 혼합 | `OrderApplicationService`가 조율만 담당, 도메인 로직은 애그리거트/도메인 서비스에 위임 |
| Vernon 규칙 3 | `customer_id`는 있으나 타입 안전성 없음 | ID 참조 유지 + 명시적 문서화 |
| Vernon 규칙 4 | 이벤트 없이 동기 처리 | `OrderConfirmedEvent`, `OrderCancelledEvent`로 결과적 일관성 지원 |
| 자기 검증 | 유효성 검사가 서비스에 분산 | `__post_init__`에서 생성 시점에 불변식 강제 |
