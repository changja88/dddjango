# 애그리거트 (Aggregate)

> 출처: [A][B][C], Vernon "Effective Aggregate Design"

연관된 엔티티와 값 객체를 하나로 묶은 개념적 단위다. 일관성 관리의 기준이 되며, 트랜잭션 경계이기도 하다.

## Vernon의 4가지 설계 규칙

**규칙 1: 진짜 불변식을 일관성 경계 안에서 보호하라**

하나의 트랜잭션에서는 하나의 애그리거트만 수정한다. 애그리거트 경계는 비즈니스 불변식(invariant)이 반드시 함께 지켜져야 하는 범위와 일치해야 한다.

**규칙 2: 작은 애그리거트를 설계하라**

> "루트 엔티티와 최소한의 속성/값 객체로 제한하라. 올바른 최소치는 일관성을 유지하는 데 필요한 만큼이며, 그 이상은 아니다." -- Vernon

**규칙 3: 다른 애그리거트는 ID로만 참조하라**

직접 객체 참조(object reference) 대신 식별자(identity)로 참조하면 결합도가 낮아지고, 로딩 시간과 메모리 사용이 줄어든다.

**규칙 4: 일관성 경계 밖에서는 결과적 일관성을 사용하라**

> **[의사결정 #4] External 채택**: 서로 다른 애그리거트 간의 일관성은 도메인 이벤트를 통한 결과적 일관성(eventual consistency)으로 달성한다.

> 실무 참고: 동일 데이터베이스 내 단순 케이스에서는 같은 트랜잭션에서 복수 애그리거트를 수정하는 것도 용인할 수 있다. 단, 이는 원칙의 예외이며 시스템이 분산되면 즉시 결과적 일관성으로 전환해야 한다.

## 값 객체와 애그리거트 구성요소

```python
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List
from uuid import uuid4


# --- 값 객체들 ---
@dataclass(frozen=True)
class OrderLineItem:
    product_id: str
    product_name: str
    price: Money
    quantity: int

    @property
    def amounts(self) -> Money:
        return self.price.multiply(self.quantity)


class OrderStatus(Enum):
    PAYMENT_WAITING = "payment_waiting"
    PREPARING = "preparing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"

    @property
    def is_shippable(self) -> bool:
        return self in (OrderStatus.PAYMENT_WAITING, OrderStatus.PREPARING)


@dataclass(frozen=True)
class ShippingInfo:
    receiver_name: str
    receiver_phone: str
    address: Address
```

## 안티패턴: 너무 큰 애그리거트 (Vernon 규칙 2 위반)

```python
# --- 나쁜 예: 너무 큰 애그리거트 (Vernon 규칙 2 위반) ---
@dataclass
class BigProduct:
    """모든 것을 하나의 애그리거트에 넣은 나쁜 예"""
    id: str
    name: str
    reviews: List["Review"] = field(default_factory=list)       # 수천 건
    images: List["ProductImage"] = field(default_factory=list)   # 수십 건
    inventory: "Inventory" = None                                # 별도 관심사
    # 리뷰 추가 시 Product 전체를 로딩하고 락을 잡아야 함 -> 성능 저하


# --- 좋은 예: 분리된 작은 애그리거트 ---
@dataclass
class Product:
    """상품 애그리거트 -- 핵심 속성만 포함"""
    id: str
    name: str
    description: str
    price: int


@dataclass
class ProductReview:
    """리뷰 애그리거트 -- Product와 ID로만 연결 (규칙 3)"""
    id: str
    product_id: str  # Product를 ID로 참조
    reviewer_id: str
    rating: int
    content: str
```

## 애그리거트 루트: 도메인 이벤트와 결과적 일관성 (규칙 4)

```python
@dataclass(frozen=True)
class OrderPlacedEvent:
    order_id: str
    customer_id: str
    total_amount: int
    occurred_at: datetime


@dataclass
class Order:
    """주문 애그리거트

    - Order가 애그리거트 루트이다
    - OrderLineItem, ShippingInfo는 애그리거트 내부 구성요소
    - 모든 상태 변경은 Order를 통해서만 수행한다
    - 다른 애그리거트(Member)는 ID로만 참조한다
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    orderer_id: str = ""  # Member 애그리거트를 ID로 참조
    order_lines: List[OrderLineItem] = field(default_factory=list)
    shipping_info: ShippingInfo = None
    _status: OrderStatus = field(default=OrderStatus.PAYMENT_WAITING)
    _events: List = field(default_factory=list)

    def __post_init__(self):
        self._verify_at_least_one_order_line()
        self._calculate_total_amounts()

    def _verify_at_least_one_order_line(self) -> None:
        if not self.order_lines:
            raise ValueError("최소 한 종류 이상의 상품을 주문해야 합니다")

    def _calculate_total_amounts(self) -> None:
        total = Money(0)
        for line in self.order_lines:
            total = total.add(line.amounts)
        self._total_amounts = total

    def change_shipping_info(self, new_info: ShippingInfo) -> None:
        if not self._status.is_shippable:
            raise ValueError("배송지를 변경할 수 없는 상태입니다")
        self.shipping_info = new_info

    def place(self) -> None:
        """주문 접수 -- 결과적 일관성을 위해 이벤트를 발행"""
        if self._status != OrderStatus.PAYMENT_WAITING:
            raise ValueError("결제 대기 상태에서만 접수할 수 있습니다")
        self._status = OrderStatus.PREPARING
        self._events.append(
            OrderPlacedEvent(
                order_id=self.id,
                customer_id=self.orderer_id,
                total_amount=self._total_amounts.amount,
                occurred_at=datetime.now(),
            )
        )

    def ship(self) -> None:
        if self._status != OrderStatus.PREPARING:
            raise ValueError("준비 상태에서만 출고할 수 있습니다")
        self._status = OrderStatus.SHIPPED

    def collect_domain_events(self) -> List:
        events = list(self._events)
        self._events.clear()
        return events


# 별도 핸들러에서 결과적 일관성으로 처리
class InventoryEventHandler:
    def handle_order_placed(self, event: OrderPlacedEvent) -> None:
        """별도 트랜잭션에서 재고 차감 -- 결과적 일관성"""
        pass

class LoyaltyEventHandler:
    def handle_order_placed(self, event: OrderPlacedEvent) -> None:
        """별도 트랜잭션에서 포인트 적립 -- 결과적 일관성"""
        pass
```

## 애그리거트를 팩토리로 사용하기 [A]

```python
@dataclass
class Store:
    """상점 애그리거트"""
    id: str
    name: str
    _is_blocked: bool = False

    def create_product(self, product_id: str, name: str, price: Money) -> "Product":
        """팩토리 메서드 - 도메인 로직(신고 차단 여부)을 애그리거트 안에 유지"""
        if self._is_blocked:
            raise PermissionError("차단된 상점은 상품을 등록할 수 없습니다")
        return Product(id=product_id, store_id=self.id, name=name, price=price)
```
