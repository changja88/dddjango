# Python 서비스 클래스 분리 기준 (SOLID 원칙 적용)

서비스 클래스가 커졌다는 것은 여러 변경 이유가 하나의 클래스에 섞여 있다는 신호다. 분리 기준은 "이 클래스가 변경되어야 하는 이유가 몇 가지인가?"에서 출발한다.

## 1단계: 변경 이유(책임)를 식별한다

클래스의 메서드를 나열하고, 각 메서드가 **누구의 요청으로 변경되는지** 그룹핑한다.

```python
# bad -- 세 가지 독립적 변경 이유가 하나의 클래스에 있다
class OrderService:
    # 그룹 A: 주문 생성 로직 (비즈니스 규칙 변경 시)
    def create_order(self, items: list[OrderItem]) -> Order: ...
    def validate_order(self, order: Order) -> None: ...

    # 그룹 B: 결제 처리 (PG사 변경 시)
    def process_payment(self, order: Order, payment: PaymentInfo) -> Receipt: ...
    def refund_payment(self, order: Order) -> RefundResult: ...

    # 그룹 C: 알림 발송 (알림 채널 변경 시)
    def send_confirmation_email(self, order: Order) -> None: ...
    def send_sms_notification(self, order: Order) -> None: ...
```

## 2단계: 변경 이유별로 클래스를 분리한다 (SRP)

```python
# good -- 각 클래스가 하나의 변경 이유만 갖는다
class OrderCreationService:
    """주문 생성과 검증을 담당한다."""

    def __init__(self, payment: PaymentService, notification: NotificationService) -> None:
        self._payment = payment
        self._notification = notification

    def create_order(self, items: list[OrderItem]) -> Order: ...
    def _validate_order(self, order: Order) -> None: ...


class PaymentService:
    """결제 처리를 담당한다."""

    def process(self, order: Order, payment: PaymentInfo) -> Receipt: ...
    def refund(self, order: Order) -> RefundResult: ...


class NotificationService:
    """주문 관련 알림 발송을 담당한다."""

    def send_confirmation(self, order: Order) -> None: ...
    def send_sms(self, order: Order) -> None: ...
```

## 3단계: 구체 구현이 아닌 Protocol에 의존한다 (DIP + ISP)

분리한 클래스 간 의존 관계를 추상화 뒤에 숨긴다. Python에서는 ABC 대신 `Protocol`로 구조적 서브타이핑을 사용한다.

```python
from typing import Protocol


class PaymentProcessor(Protocol):
    """결제 처리 인터페이스."""

    def process(self, order: Order, payment: PaymentInfo) -> Receipt: ...
    def refund(self, order: Order) -> RefundResult: ...


class Notifier(Protocol):
    """알림 발송 인터페이스."""

    def send_confirmation(self, order: Order) -> None: ...
    def send_sms(self, order: Order) -> None: ...


class OrderCreationService:
    def __init__(self, payment: PaymentProcessor, notification: Notifier) -> None:
        self._payment = payment
        self._notification = notification

    def create_order(self, items: list[OrderItem]) -> Order:
        order = Order(items=items)
        self._validate_order(order)
        return order

    def _validate_order(self, order: Order) -> None: ...
```

## 4단계: 확장에 열린 구조를 만든다 (OCP)

새로운 결제 수단이나 알림 채널이 추가될 때 기존 코드를 수정하지 않도록 한다.

```python
class StripePaymentService:
    """Stripe PG 결제 구현. PaymentProcessor Protocol을 만족한다."""

    def process(self, order: Order, payment: PaymentInfo) -> Receipt: ...
    def refund(self, order: Order) -> RefundResult: ...


class TossPaymentService:
    """Toss PG 결제 구현. 기존 코드 수정 없이 추가된다."""

    def process(self, order: Order, payment: PaymentInfo) -> Receipt: ...
    def refund(self, order: Order) -> RefundResult: ...
```

## 분리 기준 요약

| 기준 | 원칙 | 질문 |
|------|------|------|
| **변경 이유** | SRP | 이 클래스가 변경되어야 하는 이유가 2개 이상인가? |
| **변화율** | SRP | 함께 변하지 않는 메서드 그룹이 있는가? |
| **의존 방향** | DIP | 고수준 정책이 저수준 세부사항에 직접 의존하는가? |
| **인터페이스 크기** | ISP | 클라이언트가 사용하지 않는 메서드까지 알아야 하는가? |
| **확장 방식** | OCP | 새 기능 추가 시 기존 클래스를 수정해야 하는가? |

핵심은 "코드 줄 수"가 아니라 **변경 빈도와 변경 이유**로 경계를 긋는 것이다. 함께 변하는 코드는 함께 두고, 독립적으로 변하는 코드는 분리한다.

---
> **관련 스킬 참조:**
> - Protocol 기반 구조적 서브타이핑, 타입 힌트 작성 → **implementation-python** 스킬
> - SOLID 원칙 심화, God Class 분해, 리팩토링 기법 → **implementation-cleancode** 스킬
> - 분리한 서비스 클래스의 테스트 설계, 의존성 주입 테스트 → **testing** 스킬
