# 주문 관리 시스템 - 레거시 ERP 연동 설계

## 1. 문제 분석

레거시 ERP 시스템과 우리 도메인 모델 사이에 다음과 같은 불일치가 존재한다.

| 항목 | 레거시 ERP | 우리 시스템 |
|------|-----------|------------|
| 모델명 | ORD_MST, ORD_DTL | Order, OrderItem |
| 컬럼명 | CUST_CD, ITM_CD, QTY, AMT | customer, item, quantity, amount |
| 상태 | 숫자 코드 (1,2,3,4) | OrderStatus Enum |
| 날짜 | "YYYYMMDD" 문자열 | datetime |
| 금액 | float | Money 값 객체 (int 기반) |

## 2. 설계 방향: Anti-Corruption Layer (ACL)

DDD의 Anti-Corruption Layer 패턴을 적용하여 레거시 ERP의 데이터 모델이 도메인 계층으로 침투하지 않도록 격리한다.

```
[우리 도메인 모델] <--> [ACL] <--> [레거시 ERP]
```

## 3. 계층 구조

```
order/
├── domain/
│   ├── models.py          # Order, OrderItem, Customer
│   ├── value_objects.py   # Money, OrderStatus
│   └── repositories.py   # OrderRepository (인터페이스)
│
├── infrastructure/
│   └── erp/
│       ├── erp_models.py       # ERP 테이블 매핑 모델
│       ├── translators.py      # 양방향 변환기
│       └── erp_order_repository.py  # Repository 구현체
```

## 4. 도메인 모델 (변경 없음)

도메인 모델은 ERP의 존재를 전혀 모른다. 기존 그대로 유지한다.

```python
# domain/value_objects.py

from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class OrderStatus(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class Money:
    amount: int  # 원 단위 정수

    def __add__(self, other: "Money") -> "Money":
        return Money(amount=self.amount + other.amount)

    def __sub__(self, other: "Money") -> "Money":
        return Money(amount=self.amount - other.amount)


# domain/models.py

@dataclass
class Customer:
    id: str
    name: str


@dataclass
class OrderItem:
    item_code: str
    item_name: str
    quantity: int
    unit_price: Money

    @property
    def total_price(self) -> Money:
        return Money(amount=self.unit_price.amount * self.quantity)


@dataclass
class Order:
    id: str
    customer: Customer
    items: list[OrderItem]
    status: OrderStatus
    ordered_at: datetime

    @property
    def total_amount(self) -> Money:
        total = 0
        for item in self.items:
            total += item.total_price.amount
        return Money(amount=total)
```

## 5. 도메인 Repository 인터페이스

```python
# domain/repositories.py

from abc import ABC, abstractmethod

class OrderRepository(ABC):
    @abstractmethod
    def find_by_id(self, order_id: str) -> Order | None:
        ...

    @abstractmethod
    def save(self, order: Order) -> None:
        ...

    @abstractmethod
    def find_by_customer(self, customer_id: str) -> list[Order]:
        ...
```

## 6. ERP 전용 모델 (ACL 내부에만 존재)

ERP 테이블 구조를 그대로 반영하되, 이 모델은 infrastructure 계층 밖으로 절대 나가지 않는다.

```python
# infrastructure/erp/erp_models.py

from dataclasses import dataclass


@dataclass
class ErpOrderMaster:
    """ORD_MST 테이블 매핑"""
    ORD_NO: str
    CUST_CD: str
    ORD_ST: int        # 1=대기, 2=진행, 3=완료, 4=취소
    ORD_DT: str        # "YYYYMMDD"
    TOT_AMT: float


@dataclass
class ErpOrderDetail:
    """ORD_DTL 테이블 매핑"""
    ORD_NO: str
    SEQ: int
    ITM_CD: str
    ITM_NM: str
    QTY: int
    UNIT_PRC: float
    AMT: float


@dataclass
class ErpCustomer:
    """CUST_MST 테이블 매핑"""
    CUST_CD: str
    CUST_NM: str
```

## 7. Translator (변환기) -- ACL의 핵심

Translator가 두 세계 사이의 양방향 변환을 전담한다. 모든 데이터 불일치 처리 로직이 이곳에 집중된다.

```python
# infrastructure/erp/translators.py

from datetime import datetime
import math

# 상태 코드 매핑 테이블
_ERP_STATUS_TO_DOMAIN: dict[int, OrderStatus] = {
    1: OrderStatus.PENDING,
    2: OrderStatus.IN_PROGRESS,
    3: OrderStatus.COMPLETED,
    4: OrderStatus.CANCELLED,
}

_DOMAIN_STATUS_TO_ERP: dict[OrderStatus, int] = {
    v: k for k, v in _ERP_STATUS_TO_DOMAIN.items()
}


class OrderTranslator:
    """ERP 모델 <-> 도메인 모델 양방향 변환"""

    # ── ERP -> 도메인 ──

    def to_domain_order(
        self,
        erp_master: ErpOrderMaster,
        erp_details: list[ErpOrderDetail],
        erp_customer: ErpCustomer,
    ) -> Order:
        customer = self._to_domain_customer(erp_customer)
        items = [self._to_domain_item(d) for d in erp_details]
        status = self._to_domain_status(erp_master.ORD_ST)
        ordered_at = self._to_datetime(erp_master.ORD_DT)

        return Order(
            id=erp_master.ORD_NO,
            customer=customer,
            items=items,
            status=status,
            ordered_at=ordered_at,
        )

    def _to_domain_customer(self, erp: ErpCustomer) -> Customer:
        return Customer(id=erp.CUST_CD, name=erp.CUST_NM)

    def _to_domain_item(self, erp: ErpOrderDetail) -> OrderItem:
        return OrderItem(
            item_code=erp.ITM_CD,
            item_name=erp.ITM_NM,
            quantity=erp.QTY,
            unit_price=self._float_to_money(erp.UNIT_PRC),
        )

    def _to_domain_status(self, erp_status: int) -> OrderStatus:
        status = _ERP_STATUS_TO_DOMAIN.get(erp_status)
        if status is None:
            raise ValueError(f"Unknown ERP status code: {erp_status}")
        return status

    def _to_datetime(self, erp_date: str) -> datetime:
        """'YYYYMMDD' 문자열 -> datetime"""
        return datetime.strptime(erp_date, "%Y%m%d")

    def _float_to_money(self, erp_amount: float) -> Money:
        """float 금액 -> Money 값 객체 (반올림 후 정수 변환)"""
        return Money(amount=round(erp_amount))

    # ── 도메인 -> ERP ──

    def to_erp_master(self, order: Order) -> ErpOrderMaster:
        return ErpOrderMaster(
            ORD_NO=order.id,
            CUST_CD=order.customer.id,
            ORD_ST=self._to_erp_status(order.status),
            ORD_DT=self._to_erp_date(order.ordered_at),
            TOT_AMT=float(order.total_amount.amount),
        )

    def to_erp_details(self, order: Order) -> list[ErpOrderDetail]:
        details = []
        for seq, item in enumerate(order.items, start=1):
            details.append(ErpOrderDetail(
                ORD_NO=order.id,
                SEQ=seq,
                ITM_CD=item.item_code,
                ITM_NM=item.item_name,
                QTY=item.quantity,
                UNIT_PRC=float(item.unit_price.amount),
                AMT=float(item.total_price.amount),
            ))
        return details

    def _to_erp_status(self, status: OrderStatus) -> int:
        erp_code = _DOMAIN_STATUS_TO_ERP.get(status)
        if erp_code is None:
            raise ValueError(f"Cannot map status to ERP: {status}")
        return erp_code

    def _to_erp_date(self, dt: datetime) -> str:
        """datetime -> 'YYYYMMDD' 문자열"""
        return dt.strftime("%Y%m%d")
```

## 8. Repository 구현체 (ACL을 사용)

```python
# infrastructure/erp/erp_order_repository.py

class ErpOrderRepository(OrderRepository):
    """레거시 ERP를 저장소로 사용하는 Repository 구현체"""

    def __init__(self, erp_connection, translator: OrderTranslator | None = None):
        self._conn = erp_connection
        self._translator = translator or OrderTranslator()

    def find_by_id(self, order_id: str) -> Order | None:
        # 1) ERP 모델로 조회
        erp_master = self._fetch_order_master(order_id)
        if erp_master is None:
            return None

        erp_details = self._fetch_order_details(order_id)
        erp_customer = self._fetch_customer(erp_master.CUST_CD)

        # 2) Translator로 도메인 모델 변환 후 반환
        return self._translator.to_domain_order(
            erp_master, erp_details, erp_customer
        )

    def save(self, order: Order) -> None:
        # 1) 도메인 모델 -> ERP 모델 변환
        erp_master = self._translator.to_erp_master(order)
        erp_details = self._translator.to_erp_details(order)

        # 2) ERP 테이블에 저장
        self._upsert_order_master(erp_master)
        self._upsert_order_details(erp_details)

    def find_by_customer(self, customer_id: str) -> list[Order]:
        erp_masters = self._fetch_orders_by_customer(customer_id)
        orders = []
        for master in erp_masters:
            erp_details = self._fetch_order_details(master.ORD_NO)
            erp_customer = self._fetch_customer(master.CUST_CD)
            orders.append(
                self._translator.to_domain_order(
                    master, erp_details, erp_customer
                )
            )
        return orders

    # ── ERP 데이터 접근 (private) ──

    def _fetch_order_master(self, order_id: str) -> ErpOrderMaster | None:
        row = self._conn.execute(
            "SELECT ORD_NO, CUST_CD, ORD_ST, ORD_DT, TOT_AMT "
            "FROM ORD_MST WHERE ORD_NO = :ord_no",
            {"ord_no": order_id},
        ).fetchone()
        if row is None:
            return None
        return ErpOrderMaster(*row)

    def _fetch_order_details(self, order_id: str) -> list[ErpOrderDetail]:
        rows = self._conn.execute(
            "SELECT ORD_NO, SEQ, ITM_CD, ITM_NM, QTY, UNIT_PRC, AMT "
            "FROM ORD_DTL WHERE ORD_NO = :ord_no ORDER BY SEQ",
            {"ord_no": order_id},
        ).fetchall()
        return [ErpOrderDetail(*row) for row in rows]

    def _fetch_customer(self, customer_code: str) -> ErpCustomer:
        row = self._conn.execute(
            "SELECT CUST_CD, CUST_NM FROM CUST_MST WHERE CUST_CD = :cd",
            {"cd": customer_code},
        ).fetchone()
        return ErpCustomer(*row)

    def _fetch_orders_by_customer(self, customer_id: str) -> list[ErpOrderMaster]:
        rows = self._conn.execute(
            "SELECT ORD_NO, CUST_CD, ORD_ST, ORD_DT, TOT_AMT "
            "FROM ORD_MST WHERE CUST_CD = :cd",
            {"cd": customer_id},
        ).fetchall()
        return [ErpOrderMaster(*row) for row in rows]

    def _upsert_order_master(self, master: ErpOrderMaster) -> None:
        self._conn.execute(
            "MERGE INTO ORD_MST USING ... ",  # DB별 upsert 구문
            {...},
        )

    def _upsert_order_details(self, details: list[ErpOrderDetail]) -> None:
        for detail in details:
            self._conn.execute(
                "MERGE INTO ORD_DTL USING ... ",
                {...},
            )
```

## 9. 의존성 방향 요약

```
domain/models.py          <-- 어디에도 의존하지 않음 (순수)
domain/value_objects.py    <-- 어디에도 의존하지 않음 (순수)
domain/repositories.py    <-- domain 모델에만 의존 (인터페이스)
    ^
    |  (구현)
    |
infrastructure/erp/erp_order_repository.py
    |
    +--> erp_models.py     (ERP 전용, 밖으로 노출 안 됨)
    +--> translators.py    (양방향 변환 로직 집중)
```

핵심 원칙: **의존성은 항상 infrastructure -> domain 방향**이다. domain 계층은 infrastructure를 import하지 않는다.

## 10. 설계 결정 근거

### 왜 Anti-Corruption Layer인가

| 대안 | 문제점 |
|------|--------|
| 도메인 모델에 ERP 필드 추가 | 도메인이 ERP 용어로 오염됨 |
| ORM 모델을 도메인과 ERP 겸용 | 두 관심사가 결합되어 변경 이유가 두 가지가 됨 |
| ERP 모델을 직접 서비스에서 사용 | 비즈니스 로직에 float 금액, 숫자 상태코드 노출 |

### Translator를 별도 클래스로 분리한 이유

- 변환 로직이 한 곳에 집중되어 ERP 스키마 변경 시 수정 범위가 명확함
- float -> Money 반올림, 날짜 파싱 등 위험한 변환의 테스트가 용이함
- Repository가 데이터 접근에만 집중할 수 있음

### float -> Money 변환 전략

ERP의 float 금액을 `round()`로 반올림하여 정수 변환한다. 이유:
- 부동소수점 오차(예: 1000.0000001)를 안전하게 처리
- 원 단위 시스템에서 소수점 이하는 의미 없음
- 변환 손실이 발생하면 Translator 내부에서 로깅 가능
