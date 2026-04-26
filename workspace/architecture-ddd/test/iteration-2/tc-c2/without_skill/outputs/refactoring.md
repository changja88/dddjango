# 주문 할인 시스템 — 빈혈 도메인 모델을 풍부한 도메인 모델로 리팩토링

## 1. 문제 진단

기존 코드의 핵심 문제점:

- **Order**가 순수 데이터 컨테이너로, 모든 비즈니스 로직이 **OrderService**에 존재한다.
- 상태 전이 규칙(pending -> confirmed, cancelled)이 외부 서비스에 흩어져 있어, Order 객체를 직접 조작하면 불변식(invariant)이 깨진다.
- 할인 계산 로직이 서비스에 절차적으로 나열되어 있어 할인 정책 추가/변경 시 서비스 전체를 수정해야 한다.
- `total`과 `discount`를 외부에서 직접 변경할 수 있어 데이터 정합성 보장이 불가능하다.

## 2. 리팩토링 결과

```python
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List
from uuid import UUID, uuid4


# ─────────────────────────────────────────────
# Value Objects
# ─────────────────────────────────────────────

class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


class CustomerGrade(Enum):
    NORMAL = "NORMAL"
    GOLD = "GOLD"
    VIP = "VIP"

    @property
    def discount_rate(self) -> float:
        rates = {
            CustomerGrade.VIP: 0.05,
            CustomerGrade.GOLD: 0.03,
            CustomerGrade.NORMAL: 0.0,
        }
        return rates[self]


@dataclass(frozen=True)
class OrderItem:
    """주문 항목 Value Object. 불변이며 가격과 수량을 캡슐화한다."""

    name: str
    price: int
    qty: int

    def __post_init__(self) -> None:
        if self.price < 0:
            raise ValueError("가격은 0 이상이어야 합니다")
        if self.qty <= 0:
            raise ValueError("수량은 1 이상이어야 합니다")

    @property
    def line_total(self) -> int:
        return self.price * self.qty


@dataclass(frozen=True)
class Money:
    """금액을 표현하는 Value Object."""

    amount: int

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("금액은 0 이상이어야 합니다")

    def subtract(self, other: Money) -> Money:
        return Money(max(0, self.amount - other.amount))

    def add(self, other: Money) -> Money:
        return Money(self.amount + other.amount)

    def apply_rate(self, rate: float) -> Money:
        return Money(int(self.amount * rate))


# ─────────────────────────────────────────────
# Domain Policy (Strategy Pattern)
# ─────────────────────────────────────────────

class DiscountPolicy:
    """할인 정책을 캡슐화한다. 새 정책 추가 시 이 클래스만 확장하면 된다."""

    @staticmethod
    def calculate(
        subtotal: Money,
        customer_grade: CustomerGrade,
        coupon: Coupon | None = None,
    ) -> Money:
        discount = Money(0)

        # 쿠폰 할인
        if coupon is not None and coupon.is_valid():
            discount = discount.add(Money(coupon.amount))

        # 등급 할인
        grade_discount = subtotal.apply_rate(customer_grade.discount_rate)
        discount = discount.add(grade_discount)

        return discount


# ─────────────────────────────────────────────
# Aggregate Root
# ─────────────────────────────────────────────

class Order:
    """
    주문 Aggregate Root.
    모든 비즈니스 규칙을 자기 안에서 강제하며,
    외부에서 내부 상태를 직접 변경할 수 없다.
    """

    def __init__(self, id: UUID, customer_id: str, items: List[OrderItem]) -> None:
        if not items:
            raise ValueError("최소 1개 이상의 상품이 필요합니다")

        self._id = id
        self._customer_id = customer_id
        self._items = list(items)
        self._status = OrderStatus.PENDING
        self._subtotal = self._calculate_subtotal()
        self._discount = Money(0)

    # ── Factory Method ──────────────────────
    @classmethod
    def create(cls, customer_id: str, items: List[OrderItem]) -> Order:
        return cls(id=uuid4(), customer_id=customer_id, items=items)

    # ── Read-only Properties ────────────────
    @property
    def id(self) -> UUID:
        return self._id

    @property
    def customer_id(self) -> str:
        return self._customer_id

    @property
    def items(self) -> tuple[OrderItem, ...]:
        return tuple(self._items)

    @property
    def status(self) -> OrderStatus:
        return self._status

    @property
    def subtotal(self) -> Money:
        return self._subtotal

    @property
    def discount(self) -> Money:
        return self._discount

    @property
    def total(self) -> Money:
        return self._subtotal.subtract(self._discount)

    # ── Commands (비즈니스 행위) ─────────────

    def apply_discount(
        self,
        customer_grade: CustomerGrade,
        coupon: Coupon | None = None,
    ) -> None:
        """할인을 적용한다. 할인 정책의 계산 결과를 주문이 받아들인다."""
        if self._status != OrderStatus.PENDING:
            raise ValueError("대기 상태에서만 할인을 적용할 수 있습니다")

        self._discount = DiscountPolicy.calculate(
            subtotal=self._subtotal,
            customer_grade=customer_grade,
            coupon=coupon,
        )

    def confirm(self) -> None:
        """주문을 확정한다."""
        self._ensure_status(
            allowed={OrderStatus.PENDING},
            message="대기 상태만 확정 가능합니다",
        )
        self._status = OrderStatus.CONFIRMED

    def cancel(self) -> None:
        """주문을 취소한다."""
        not_allowed = {OrderStatus.SHIPPED, OrderStatus.CANCELLED}
        if self._status in not_allowed:
            raise ValueError("취소 불가능한 상태입니다")
        self._status = OrderStatus.CANCELLED

    # ── Private Helpers ─────────────────────

    def _calculate_subtotal(self) -> Money:
        return Money(sum(item.line_total for item in self._items))

    def _ensure_status(self, allowed: set[OrderStatus], message: str) -> None:
        if self._status not in allowed:
            raise ValueError(message)


# ─────────────────────────────────────────────
# 외부 의존 객체 (참고용 인터페이스)
# ─────────────────────────────────────────────

@dataclass
class Coupon:
    code: str
    amount: int
    _valid: bool = True

    def is_valid(self) -> bool:
        return self._valid
```

## 3. 변경 요약

| 관점 | Before (빈혈 모델) | After (풍부한 모델) |
|------|-------------------|-------------------|
| **데이터 보호** | 모든 필드가 public, 외부에서 자유롭게 변경 | 필드를 `_` 접두사로 보호하고 read-only property 제공 |
| **비즈니스 로직 위치** | `OrderService`에 절차적으로 나열 | `Order` Aggregate Root 내부에 캡슐화 |
| **상태 전이** | 서비스가 `order.status = "confirmed"` 직접 대입 | `order.confirm()` 메서드가 전이 규칙을 강제 |
| **불변식 보장** | 없음 (빈 items로 주문 생성 가능) | 생성자에서 최소 1개 상품 검증 |
| **할인 계산** | 서비스에 if/elif 분기 | `DiscountPolicy` 분리 + `CustomerGrade` enum에 할인율 내장 |
| **금액 표현** | 원시 `int` | `Money` Value Object로 연산 캡슐화 |
| **주문 항목** | `dict` (타입 안전성 없음) | `OrderItem` frozen dataclass (불변, 검증 포함) |
| **total 정합성** | `discount`와 `total`을 각각 수동 갱신 | `total`은 항상 `subtotal - discount`로 계산하는 파생 프로퍼티 |

## 4. 핵심 설계 판단

**a) total을 파생 프로퍼티로 변경**

기존 코드에서 `total`과 `discount`를 별도로 관리하면 둘 사이의 정합성이 깨질 위험이 있다. `total`을 항상 `subtotal - discount`로 계산하는 프로퍼티로 만들어 이 문제를 원천 차단했다.

**b) DiscountPolicy 분리**

할인 로직을 Order 내부에 직접 넣지 않고 별도 정책 객체로 분리했다. Order는 "할인을 적용받는다"는 행위만 알고, 구체적인 할인 계산 방법은 DiscountPolicy에 위임한다. 향후 할인 정책이 복잡해지면 Strategy 패턴으로 다형성 확장이 가능하다.

**c) 상태 전이를 명시적 메서드로 표현**

`confirm()`, `cancel()` 같은 명령 메서드가 상태 전이의 유일한 진입점이 되어, 잘못된 상태 전이를 컴파일 타임에 가까운 수준에서 방지한다.
