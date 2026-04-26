# C01: 주문 도메인을 설계부터 Django Ninja 구현까지 전체 과정 안내

**Skill:** architecture-ddd (설계 mode)
**Cross-skill references loaded:** implementation-django-ninja (Schema, Router), implementation-django (모델), architecture-api (URL 설계)

## [주요 내용]

### 1단계: 전략적 설계 (DDD 우선)

**바운디드 컨텍스트 식별:**
- 주문(Order) 컨텍스트: 주문 생성, 상태 관리, 주문 항목
- 결제(Payment) 컨텍스트: 결제 처리, 환불
- 배송(Shipping) 컨텍스트: 배송 추적, 배송지 관리

컨텍스트 간 통신은 도메인 이벤트로 결과적 일관성을 달성한다.

### 2단계: 전술적 설계 (애그리거트)

```python
# domain/order/aggregates.py
@dataclass(frozen=True)
class Money:
    amount: int
    currency: str = "KRW"
    def add(self, other: "Money") -> "Money":
        assert self.currency == other.currency
        return Money(self.amount + other.amount, self.currency)

@dataclass(frozen=True)
class OrderLineItem:
    product_id: str
    product_name: str
    price: Money
    quantity: int

@dataclass
class Order:
    """주문 애그리거트 루트 -- Vernon 4규칙 적용"""
    id: str
    orderer_id: str  # ID 참조 (규칙 3)
    order_lines: list[OrderLineItem]
    _status: OrderStatus = OrderStatus.PENDING
    _events: list = field(default_factory=list)

    def place(self) -> None:
        self._status = OrderStatus.CONFIRMED
        self._events.append(OrderPlacedEvent(order_id=self.id))

    def cancel(self) -> None:
        if self._status != OrderStatus.PENDING:
            raise ValueError("대기 상태에서만 취소 가능")
        self._status = OrderStatus.CANCELLED
```

### 3단계: 리포지토리 인터페이스

```python
# domain/order/repositories.py
class OrderRepository(ABC):
    @abstractmethod
    def find_by_id(self, order_id: str) -> Order | None: ...
    @abstractmethod
    def save(self, order: Order) -> None: ...
```

### 4단계: Django 모델 (implementation-django 위임)

```python
# apps/orders/models.py
class OrderModel(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending"
        CONFIRMED = "confirmed"
        CANCELLED = "cancelled"

    orderer_id = models.CharField(max_length=36)
    status = models.CharField(max_length=20, choices=Status.choices)
    created_at = models.DateTimeField(auto_now_add=True)
```

### 5단계: Django Ninja API (implementation-django-ninja 위임)

```python
# apps/orders/api.py
from ninja import Router, Schema

router = Router(tags=["orders"])

class OrderOut(Schema):
    id: int
    status: str
    total: int
    created_at: datetime

@router.post("/", response={201: OrderOut})
def create_order(request, payload: OrderIn):
    order = order_service.place_order(payload)
    return 201, order

@router.post("/{order_id}/cancel", response={200: OrderOut})
def cancel_order(request, order_id: int):
    order = order_service.cancel_order(order_id)
    return order
```

---
> **관련 스킬 참조:**
> - [Django Ninja Schema, Router, 인증] → **implementation-django-ninja** 스킬
> - [Django 모델 설계, QuerySet] → **implementation-django** 스킬
> - [REST URL 설계, 상태 코드] → **architecture-api** 스킬
> - [헥사고날, CQRS 아키텍처] → **architecture-implementation-patterns** 스킬
