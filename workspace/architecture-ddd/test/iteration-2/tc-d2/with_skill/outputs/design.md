# 주문 관리 시스템 - 레거시 ERP 연동 설계

## 1. 전략 설계: 바운디드 컨텍스트와 컨텍스트 맵

### 바운디드 컨텍스트 식별

두 시스템은 서로 다른 바운디드 컨텍스트에 속한다.

| 컨텍스트 | 유비쿼터스 언어 | 모델 특성 |
|---------|---------------|----------|
| **주문 관리 (Order Management)** | Order, OrderItem, Customer, OrderStatus, Money | 도메인 용어 기반, 타입 안전, 불변식 보호 |
| **레거시 ERP** | ORD_MST, ORD_DTL, CUST_CD, STAT_CD, AMT | 축약형 테이블/컬럼명, 숫자 상태 코드, float 금액 |

같은 "주문"이라는 개념이 두 컨텍스트에서 완전히 다른 언어와 구조로 표현된다. 이것이 바운디드 컨텍스트 경계의 명확한 근거다.

### 컨텍스트 맵: 충돌 방지 계층(ACL) 패턴 선택

```
[레거시 ERP]  ──(Upstream)──  ACL  ──(Downstream)──  [주문 관리 컨텍스트]
```

- **관계 유형**: 고객-공급자 (Customer-Supplier). 레거시 ERP는 업스트림(공급자)이며, 우리 시스템은 다운스트림(고객)이다.
- **통합 패턴**: **충돌 방지 계층(Anti-Corruption Layer)**. 레거시 ERP의 모델이 우리 도메인과 맞지 않으므로, ACL이 업스트림 모델을 우리 모델로 변환하여 도메인 오염을 차단한다.

ACL을 선택하는 이유:
1. 레거시 ERP는 우리가 변경할 수 없는 외부 시스템이다 (순응주의자 또는 ACL 중 선택).
2. ERP의 축약형 명명, 숫자 상태 코드, float 금액, YYYYMMDD 문자열은 우리 도메인 언어와 완전히 다르다.
3. 순응주의자 패턴을 택하면 레거시 모델이 도메인 전체를 오염시킨다. ACL로 번역 계층을 두어 도메인의 순수성을 보호해야 한다.

---

## 2. 전술 설계: 도메인 모델 (우리 시스템)

우리 도메인 모델은 레거시 ERP의 존재를 전혀 모른다. 유비쿼터스 언어를 그대로 반영하며, 풍부한 도메인 모델을 지향한다.

### 값 객체

```python
from dataclasses import dataclass, replace
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Money:
    """금액 값 객체 -- int 기반으로 부동소수점 오차를 원천 차단"""
    amount: int
    currency: str = "KRW"

    def __post_init__(self) -> None:
        if not isinstance(self.amount, int):
            object.__setattr__(self, "amount", int(self.amount))
        if self.amount < 0:
            raise ValueError(f"금액은 0 이상이어야 합니다: {self.amount}")

    def add(self, other: "Money") -> "Money":
        self._ensure_same_currency(other)
        return replace(self, amount=self.amount + other.amount)

    def subtract(self, other: "Money") -> "Money":
        self._ensure_same_currency(other)
        result = self.amount - other.amount
        if result < 0:
            raise ValueError("결과 금액이 음수입니다")
        return replace(self, amount=result)

    def multiply(self, factor: int) -> "Money":
        return replace(self, amount=self.amount * factor)

    def _ensure_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError(f"통화 불일치: {self.currency} != {other.currency}")


@dataclass(frozen=True, slots=True)
class OrderLineItem:
    """주문 항목 값 객체"""
    product_id: str
    product_name: str
    unit_price: Money
    quantity: int

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError(f"수량은 1 이상이어야 합니다: {self.quantity}")

    @property
    def line_total(self) -> Money:
        return self.unit_price.multiply(self.quantity)
```

### 엔티티와 애그리거트

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import List
from uuid import uuid4


class OrderStatus(Enum):
    """주문 상태 -- 비즈니스 의도를 드러내는 이름 사용"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    @property
    def is_cancellable(self) -> bool:
        return self in (OrderStatus.PENDING, OrderStatus.PROCESSING)


@dataclass
class Order:
    """주문 애그리거트 루트

    - 비즈니스 로직이 엔티티 안에 위치한다 (풍부한 도메인 모델)
    - Customer는 ID로만 참조한다 (Vernon 규칙 3)
    - 레거시 ERP의 존재를 전혀 모른다
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    customer_id: str = ""
    items: List[OrderLineItem] = field(default_factory=list)
    _status: OrderStatus = field(default=OrderStatus.PENDING)
    ordered_at: datetime = field(default_factory=datetime.now)
    _events: List = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.items:
            raise ValueError("최소 한 개의 주문 항목이 필요합니다")

    @property
    def status(self) -> OrderStatus:
        return self._status

    @property
    def total_amount(self) -> Money:
        total = Money(0)
        for item in self.items:
            total = total.add(item.line_total)
        return total

    def process(self) -> None:
        """주문 진행 -- 비즈니스 의도를 드러내는 메서드명"""
        if self._status != OrderStatus.PENDING:
            raise ValueError(f"{self._status.value} 상태에서는 진행할 수 없습니다")
        self._status = OrderStatus.PROCESSING

    def complete(self) -> None:
        """주문 완료"""
        if self._status != OrderStatus.PROCESSING:
            raise ValueError(f"{self._status.value} 상태에서는 완료할 수 없습니다")
        self._status = OrderStatus.COMPLETED

    def cancel(self) -> None:
        """주문 취소"""
        if not self._status.is_cancellable:
            raise ValueError(f"{self._status.value} 상태에서는 취소할 수 없습니다")
        self._status = OrderStatus.CANCELLED
```

---

## 3. 충돌 방지 계층(ACL) 설계

ACL은 인프라 계층에 위치한다. 레거시 ERP의 데이터 구조를 우리 도메인 모델로 번역하고, 반대 방향 번역도 담당한다.

### 패키지 구조

```
src/
├── ordering/
│   ├── domain/
│   │   ├── model.py             # Order, OrderLineItem, OrderStatus, Money
│   │   ├── events.py            # 도메인 이벤트
│   │   └── repository.py        # OrderRepository ABC
│   │
│   ├── application/
│   │   └── services.py          # 응용 서비스 (유스케이스 조율)
│   │
│   └── infrastructure/
│       ├── repository.py        # OrderRepository 구현체
│       ├── erp/                 # 레거시 ERP 연동 전담 모듈
│       │   ├── __init__.py
│       │   ├── dto.py           # ERP 데이터 구조 (DTO)
│       │   ├── translator.py    # ACL 번역기
│       │   ├── client.py        # ERP 통신 클라이언트
│       │   └── adapter.py       # ERP 어댑터 (포트 구현체)
│       └── ...
```

핵심 의존성 규칙: `domain/`은 `infrastructure/erp/`에 절대 의존하지 않는다. ERP 관련 코드는 전부 인프라 계층에 격리된다.

### ERP 데이터 구조 (DTO)

레거시 ERP의 데이터 구조를 있는 그대로 표현한다. 이 클래스들은 도메인 모델이 아니라 데이터 전송 객체다.

```python
# ordering/infrastructure/erp/dto.py
from dataclasses import dataclass


@dataclass
class ERPOrderMaster:
    """레거시 ERP 주문 마스터 (ORD_MST) 테이블 구조를 그대로 반영"""
    ORD_NO: str       # 주문번호
    CUST_CD: str      # 고객코드
    ORD_DT: str       # 주문일자 ("YYYYMMDD")
    TOT_AMT: float    # 총금액 (float)
    STAT_CD: int      # 상태코드 (1=대기, 2=진행, 3=완료, 4=취소)


@dataclass
class ERPOrderDetail:
    """레거시 ERP 주문 상세 (ORD_DTL) 테이블 구조를 그대로 반영"""
    ORD_NO: str       # 주문번호
    SEQ_NO: int       # 순번
    ITM_CD: str       # 상품코드
    ITM_NM: str       # 상품명
    QTY: int          # 수량
    AMT: float        # 금액 (float)
```

### ACL 번역기 (Translator)

번역기가 모든 타입 변환, 값 매핑, 형식 변환을 수행한다. 이 계층이 레거시 ERP의 "오염"을 흡수하여 도메인을 보호한다.

```python
# ordering/infrastructure/erp/translator.py
from datetime import datetime
from typing import List

from ordering.domain.model import (
    Money,
    Order,
    OrderLineItem,
    OrderStatus,
)
from ordering.infrastructure.erp.dto import ERPOrderDetail, ERPOrderMaster


class ERPOrderTranslator:
    """충돌 방지 계층(ACL) -- 레거시 ERP 모델과 도메인 모델 간 양방향 번역

    번역 대상:
    - 축약형 필드명 -> 도메인 용어 (ORD_NO -> id, CUST_CD -> customer_id)
    - 숫자 상태 코드 -> OrderStatus Enum (1 -> PENDING, 2 -> PROCESSING, ...)
    - "YYYYMMDD" 문자열 -> datetime 객체
    - float 금액 -> Money 값 객체 (int 기반)
    """

    # ERP 상태 코드 -> 도메인 OrderStatus 매핑
    _STATUS_FROM_ERP = {
        1: OrderStatus.PENDING,
        2: OrderStatus.PROCESSING,
        3: OrderStatus.COMPLETED,
        4: OrderStatus.CANCELLED,
    }

    # 도메인 OrderStatus -> ERP 상태 코드 매핑 (역방향)
    _STATUS_TO_ERP = {v: k for k, v in _STATUS_FROM_ERP.items()}

    # --- ERP -> 도메인 (인바운드 번역) ---

    def to_domain_order(
        self,
        erp_master: ERPOrderMaster,
        erp_details: List[ERPOrderDetail],
    ) -> Order:
        """ERP 주문 데이터를 도메인 Order 애그리거트로 번역"""
        items = [self._to_domain_item(detail) for detail in erp_details]
        status = self._to_domain_status(erp_master.STAT_CD)
        ordered_at = self._to_datetime(erp_master.ORD_DT)

        return Order(
            id=erp_master.ORD_NO,
            customer_id=erp_master.CUST_CD,
            items=items,
            _status=status,
            ordered_at=ordered_at,
        )

    def _to_domain_item(self, erp_detail: ERPOrderDetail) -> OrderLineItem:
        """ERP 주문 상세를 도메인 OrderLineItem 값 객체로 번역"""
        return OrderLineItem(
            product_id=erp_detail.ITM_CD,
            product_name=erp_detail.ITM_NM,
            unit_price=self._to_money(erp_detail.AMT),
            quantity=erp_detail.QTY,
        )

    def _to_domain_status(self, stat_cd: int) -> OrderStatus:
        """ERP 숫자 상태 코드를 도메인 OrderStatus Enum으로 번역"""
        status = self._STATUS_FROM_ERP.get(stat_cd)
        if status is None:
            raise ValueError(f"알 수 없는 ERP 상태 코드: {stat_cd}")
        return status

    def _to_money(self, erp_amount: float) -> Money:
        """ERP float 금액을 Money 값 객체(int 기반)로 번역

        float -> int 변환 시 반올림으로 부동소수점 오차를 보정한다.
        """
        return Money(amount=round(erp_amount))

    def _to_datetime(self, erp_date: str) -> datetime:
        """ERP "YYYYMMDD" 문자열을 datetime으로 번역"""
        return datetime.strptime(erp_date, "%Y%m%d")

    # --- 도메인 -> ERP (아웃바운드 번역) ---

    def to_erp_master(self, order: Order) -> ERPOrderMaster:
        """도메인 Order를 ERP 주문 마스터 구조로 역번역"""
        return ERPOrderMaster(
            ORD_NO=order.id,
            CUST_CD=order.customer_id,
            ORD_DT=order.ordered_at.strftime("%Y%m%d"),
            TOT_AMT=float(order.total_amount.amount),
            STAT_CD=self._to_erp_status(order.status),
        )

    def to_erp_details(self, order: Order) -> List[ERPOrderDetail]:
        """도메인 OrderLineItem 목록을 ERP 주문 상세 구조로 역번역"""
        details = []
        for seq, item in enumerate(order.items, start=1):
            details.append(
                ERPOrderDetail(
                    ORD_NO=order.id,
                    SEQ_NO=seq,
                    ITM_CD=item.product_id,
                    ITM_NM=item.product_name,
                    QTY=item.quantity,
                    AMT=float(item.unit_price.amount),
                )
            )
        return details

    def _to_erp_status(self, status: OrderStatus) -> int:
        """도메인 OrderStatus를 ERP 숫자 상태 코드로 역번역"""
        erp_code = self._STATUS_TO_ERP.get(status)
        if erp_code is None:
            raise ValueError(f"ERP에 매핑할 수 없는 상태: {status}")
        return erp_code
```

### ERP 어댑터

어댑터는 도메인의 리포지토리 인터페이스나 포트를 구현하여, 응용 서비스가 ERP의 존재를 의식하지 않고 도메인 객체만 다루게 한다.

```python
# ordering/infrastructure/erp/adapter.py
from abc import ABC, abstractmethod
from typing import List, Optional

from ordering.domain.model import Order
from ordering.infrastructure.erp.client import ERPClient
from ordering.infrastructure.erp.translator import ERPOrderTranslator


# 도메인 계층에 정의되는 포트 (ABC)
class ERPOrderPort(ABC):
    """ERP 주문 동기화를 위한 포트 -- 도메인 계층에 정의"""

    @abstractmethod
    def fetch_order(self, order_id: str) -> Optional[Order]:
        ...

    @abstractmethod
    def sync_order(self, order: Order) -> None:
        ...


# 인프라 계층의 어댑터 구현
class ERPOrderAdapter(ERPOrderPort):
    """ERP 어댑터 -- ACL을 사용하여 ERP 통신을 도메인 모델로 추상화

    응용 서비스는 이 어댑터를 통해 ERP와 통신하지만,
    ERP의 데이터 구조(DTO)를 직접 다루지 않는다.
    Translator가 모든 변환을 담당한다.
    """

    def __init__(self, client: ERPClient, translator: ERPOrderTranslator):
        self._client = client
        self._translator = translator

    def fetch_order(self, order_id: str) -> Optional[Order]:
        """ERP에서 주문을 조회하여 도메인 Order로 반환"""
        erp_master = self._client.get_order_master(order_id)
        if erp_master is None:
            return None
        erp_details = self._client.get_order_details(order_id)
        return self._translator.to_domain_order(erp_master, erp_details)

    def sync_order(self, order: Order) -> None:
        """도메인 Order를 ERP 형식으로 변환하여 ERP에 동기화"""
        erp_master = self._translator.to_erp_master(order)
        erp_details = self._translator.to_erp_details(order)
        self._client.upsert_order(erp_master, erp_details)

    def fetch_orders_by_status(self, status_code: int) -> List[Order]:
        """ERP 상태 코드로 주문 목록을 조회하여 도메인 Order 목록으로 반환"""
        results = []
        erp_orders = self._client.get_orders_by_status(status_code)
        for erp_master in erp_orders:
            erp_details = self._client.get_order_details(erp_master.ORD_NO)
            order = self._translator.to_domain_order(erp_master, erp_details)
            results.append(order)
        return results
```

### 응용 서비스에서의 사용

응용 서비스는 도메인 객체만 다루며, ERP의 데이터 구조를 전혀 알지 못한다.

```python
# ordering/application/services.py
from ordering.domain.model import Order
from ordering.domain.repository import OrderRepository
from ordering.infrastructure.erp.adapter import ERPOrderPort


class OrderSyncService:
    """주문 ERP 동기화 응용 서비스

    - 비즈니스 로직은 Order 애그리거트에 위임한다
    - ERP 통신은 ERPOrderPort(어댑터)에 위임한다
    - 이 서비스는 흐름만 조율한다
    """

    def __init__(
        self,
        order_repository: OrderRepository,
        erp_port: ERPOrderPort,
    ):
        self._order_repo = order_repository
        self._erp_port = erp_port

    def import_order_from_erp(self, erp_order_id: str) -> str:
        """ERP 주문을 우리 시스템으로 가져온다"""
        order = self._erp_port.fetch_order(erp_order_id)
        if order is None:
            raise ValueError(f"ERP에서 주문을 찾을 수 없습니다: {erp_order_id}")
        self._order_repo.save(order)
        return order.id

    def export_order_to_erp(self, order_id: str) -> None:
        """우리 시스템의 주문을 ERP에 동기화한다"""
        order = self._order_repo.find_by_id(order_id)
        if order is None:
            raise ValueError(f"주문을 찾을 수 없습니다: {order_id}")
        self._erp_port.sync_order(order)
```

---

## 4. 설계 원칙 요약

### 적용된 DDD 원칙

| 원칙 | 적용 내용 |
|------|----------|
| **전략 설계 우선** | 바운디드 컨텍스트 경계를 먼저 정의한 후 전술 패턴을 적용했다 |
| **충돌 방지 계층(ACL)** | Translator가 ERP 모델을 도메인 모델로 양방향 번역하여 오염을 차단한다 |
| **유비쿼터스 언어** | 도메인 모델은 `Order`, `cancel()`, `complete()` 같은 비즈니스 용어를 사용한다. `updateStatus()`가 아닌 비즈니스 의도를 드러내는 메서드명을 사용한다 |
| **값 객체 우선** | Money, OrderLineItem을 불변 값 객체로 설계하여 부작용을 제거했다 |
| **풍부한 도메인 모델** | 상태 전이 규칙(`cancel()`, `process()`, `complete()`)이 Order 엔티티 안에 있다 |
| **ID 참조 (Vernon 규칙 3)** | Customer를 `customer_id: str`로 참조한다 |
| **의존성 역전** | 도메인이 인터페이스(포트)를 정의하고, 인프라가 구현(어댑터)을 제공한다 |

### 오염 방지 경계 정리

레거시 ERP의 특성이 도메인 모델에 유입되지 않도록 ACL이 차단하는 항목:

| ERP 특성 | ACL 번역 | 도메인 모델 |
|---------|---------|-----------|
| `ORD_MST`, `ORD_DTL` (축약 테이블명) | ERPOrderMaster/ERPOrderDetail DTO로 격리 | `Order`, `OrderLineItem` |
| `CUST_CD`, `ITM_CD` (축약 컬럼명) | Translator가 필드명 매핑 | `customer_id`, `product_id` |
| `STAT_CD` = 1,2,3,4 (숫자 상태 코드) | `_STATUS_FROM_ERP` 딕셔너리로 매핑 | `OrderStatus` Enum |
| `ORD_DT` = "YYYYMMDD" (문자열 날짜) | `strptime`/`strftime` 변환 | `datetime` 객체 |
| `AMT` = float (부동소수점 금액) | `round()` 후 `Money(int)` 변환 | `Money` 값 객체 (int 기반) |

### 핵심 설계 결정

1. **Translator를 별도 클래스로 분리한다.** 어댑터 안에 변환 로직을 인라인하지 않고, Translator를 독립 클래스로 만들어 단위 테스트를 용이하게 한다. 매핑 규칙이 변경되면 Translator만 수정하면 된다.

2. **양방향 번역을 지원한다.** ERP에서 읽어오는 인바운드(`to_domain_order`)와 ERP로 내보내는 아웃바운드(`to_erp_master`, `to_erp_details`) 번역을 모두 하나의 Translator에서 관리하여 매핑 일관성을 보장한다.

3. **ERP DTO는 ERP의 구조를 있는 그대로 반영한다.** DTO에서 이름을 도메인 용어로 바꾸지 않는다. `ORD_NO`, `CUST_CD`, `STAT_CD` 같은 원래 이름을 유지하여, ERP 측 변경 사항을 추적하기 쉽게 한다. 번역은 오직 Translator의 책임이다.

4. **float -> int 변환 시 `round()`를 사용한다.** ERP의 float 금액은 부동소수점 오차를 포함할 수 있다(예: 10000.0이 9999.999999로 표현). `int()`가 아닌 `round()`로 반올림하여 이 오차를 보정한 후 Money 값 객체에 담는다.
