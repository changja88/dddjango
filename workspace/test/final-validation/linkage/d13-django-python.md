# D13: Cross-Skill Delegation -- implementation-django -> implementation-python

## Prompt
"Django 서비스 레이어에서 타입 힌트를 어떻게 활용하면 좋을까? Protocol이나 제네릭도 쓰고 싶은데."

## Skill
`implementation-django` (source) -> `implementation-python` (delegated)

## Response

서비스 레이어의 구조는 **implementation-django**가 다루지만, 타입 힌트 체계(Protocol, 제네릭, PEP 695)는 **implementation-python**의 영역이다. 아래는 Django 서비스 레이어에 현대적 Python 타입 시스템을 결합하는 패턴이다.

### 1. 서비스 함수에 키워드 전용 매개변수 + 타입 힌트

Django 서비스 레이어의 `<entity>_<action>` 네이밍과 Python의 키워드 전용(`*`) 매개변수를 결합한다. 호출자가 인자 순서를 실수할 수 없게 만든다.

```python
from django.db import transaction

def order_create(
    *,
    user: User,
    items: list[OrderItem],
    coupon: Coupon | None = None,
) -> Order:
    """주문을 생성하고 재고를 차감한다."""
    with transaction.atomic():
        order = Order.objects.create(user=user)
        _apply_items(order=order, items=items)
        if coupon:
            _apply_coupon(order=order, coupon=coupon)

    transaction.on_commit(lambda: send_confirmation_email(order))
    return order


def order_cancel(*, order: Order, reason: str) -> Order:
    """주문을 취소하고 재고를 복원한다."""
    if order.status != Order.Status.CONFIRMED:
        raise ValidationError("취소할 수 없는 상태입니다.")
    order.status = Order.Status.CANCELLED
    order.cancel_reason = reason
    order.save(update_fields=["status", "cancel_reason", "updated_at"])
    return order
```

핵심 포인트:
- 모든 매개변수를 `*` 뒤에 배치하여 키워드 전용으로 강제한다.
- 반환 타입을 명시하여 호출자가 결과 타입을 추론할 필요 없게 한다.
- `X | None`을 사용한다. `Optional[X]`는 레거시다 (3.10+).

### 2. Protocol로 외부 의존성 추상화

서비스 레이어가 결제, 알림 같은 외부 시스템에 의존할 때, ABC 대신 `Protocol`을 사용하여 구조적 서브타이핑으로 계약을 정의한다. 상속 없이 구조만 맞으면 통과한다.

```python
from typing import Protocol
from decimal import Decimal


class PaymentGateway(Protocol):
    """결제 처리 인터페이스."""

    def charge(self, *, amount: Decimal, token: str) -> PaymentResult: ...
    def refund(self, *, payment_id: str) -> RefundResult: ...


class NotificationSender(Protocol):
    """알림 발송 인터페이스."""

    def send(self, *, recipient: str, message: str) -> None: ...


# 구현체 -- Protocol을 상속하지 않는다
class TossPaymentService:
    def charge(self, *, amount: Decimal, token: str) -> PaymentResult:
        # Toss API 호출
        ...

    def refund(self, *, payment_id: str) -> RefundResult:
        # Toss 환불 처리
        ...


class KakaoNotificationService:
    def send(self, *, recipient: str, message: str) -> None:
        # 카카오 알림톡 발송
        ...
```

핵심 포인트:
- Protocol은 덕 타이핑과 정적 타입 체커를 연결한다.
- 구현체가 Protocol을 상속할 필요가 없어 결합도가 낮다.
- 테스트에서 Fake 객체를 쉽게 만들 수 있다.

### 3. Protocol 합성으로 인터페이스 분리

클라이언트가 사용하지 않는 메서드를 알 필요 없게, 작은 Protocol을 합성한다.

```python
class Chargeable(Protocol):
    def charge(self, *, amount: Decimal, token: str) -> PaymentResult: ...


class Refundable(Protocol):
    def refund(self, *, payment_id: str) -> RefundResult: ...


class FullPaymentGateway(Chargeable, Refundable, Protocol):
    """결제와 환불 모두 가능한 게이트웨이."""
    ...


# 결제만 필요한 서비스는 Chargeable만 요구한다
def order_create(
    *,
    user: User,
    items: list[OrderItem],
    payment: Chargeable,
) -> Order:
    ...


# 환불만 필요한 서비스는 Refundable만 요구한다
def order_refund(
    *,
    order: Order,
    gateway: Refundable,
) -> RefundResult:
    ...
```

### 4. PEP 695 제네릭으로 범용 서비스 패턴

여러 엔티티에 걸쳐 반복되는 서비스 패턴을 제네릭으로 추상화한다. 3.12+ PEP 695 구문을 사용한다.

```python
from django.db import models


# 제네릭 결과 타입
@dataclass(frozen=True, slots=True)
class ServiceResult[T]:
    """서비스 실행 결과를 담는 제네릭 컨테이너."""
    data: T
    warnings: list[str] = field(default_factory=list)


# 제네릭 셀렉터 Protocol
class EntitySelector[M: models.Model](Protocol):
    """엔티티 조회 인터페이스."""

    def get_by_id(self, *, pk: int) -> M: ...
    def get_list(self, *, filters: dict[str, object]) -> models.QuerySet[M]: ...


# 구체 셀렉터
class OrderSelector:
    def get_by_id(self, *, pk: int) -> Order:
        return Order.objects.select_related("user").get(pk=pk)

    def get_list(self, *, filters: dict[str, object]) -> models.QuerySet[Order]:
        return Order.objects.filter(**filters).order_by("-created_at")


# 서비스 함수에서 활용
def order_create(
    *,
    user: User,
    items: list[OrderItem],
) -> ServiceResult[Order]:
    """주문을 생성하고 결과를 ServiceResult로 감싼다."""
    warnings: list[str] = []
    with transaction.atomic():
        order = Order.objects.create(user=user)
        for item in items:
            if item.stock < 10:
                warnings.append(f"{item.name} 재고가 부족합니다.")
            OrderLine.objects.create(order=order, item=item)
    return ServiceResult(data=order, warnings=warnings)
```

핵심 포인트:
- `class ServiceResult[T]`는 PEP 695 구문이다. `TypeVar` 전역 선언이 필요 없다.
- `M: models.Model`은 상한 제약(bound)으로, Model 하위 타입만 허용한다.
- `ServiceResult`를 `frozen=True`로 만들어 불변 값 객체로 사용한다.

### 5. type alias로 도메인 타입 표현

`type` 문(3.12+)으로 도메인 의미를 가진 타입 별칭을 선언한다.

```python
from decimal import Decimal

type Money = Decimal
type Email = str
type OrderId = int

def order_total(*, order_id: OrderId) -> Money:
    """주문의 총 금액을 반환한다."""
    order = Order.objects.prefetch_related("lines__item").get(pk=order_id)
    return Money(sum(line.subtotal for line in order.lines.all()))
```

더 강한 타입 안전성이 필요하면 `NewType`을 사용한다:

```python
from typing import NewType

OrderId = NewType("OrderId", int)
Money = NewType("Money", Decimal)

# OrderId(42)는 OK, 순수 int 전달은 타입 체커 에러
def order_total(*, order_id: OrderId) -> Money: ...
```

---
> **관련 스킬 참조:**
> - [Protocol, 제네릭, PEP 695 타입 시스템 심화] -> **implementation-python** 스킬
> - [서비스 레이어 도입 시점과 트랜잭션 패턴] -> **implementation-django** 스킬
> - [SOLID 원칙 기반 서비스 분리, DIP 적용] -> **implementation-cleancode** 스킬
> - [헥사고날 아키텍처, CQRS 패턴으로의 확장] -> **architecture-implementation-patterns** 스킬
> - [서비스 레이어 단위 테스트, Protocol Mock 전략] -> **testing** 스킬
