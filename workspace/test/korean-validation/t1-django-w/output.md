# Django 프로젝트에서 헥사고날 아키텍처 도입 설계

## 설계 전 복잡도 평가

헥사고날 아키텍처를 도입하기 전에 먼저 복잡도를 평가한다. 단순 CRUD라면 레이어드 아키텍처로 충분하며, 외부 통합이 다수이고 진입점이 다양한 복잡한 도메인일 때 헥사고날이 적합하다. 모든 곳에 헥사고날을 강제하지 않는다.

헥사고날 도입이 정당화되는 상황:
- 외부 시스템 통합이 3개 이상 (결제, 알림, 외부 API 등)
- 동일 비즈니스 로직에 여러 진입점 (웹, CLI, Celery 워커 등)
- 인프라 교체 가능성이 높은 경우 (DB, 메시지 브로커 등)
- 도메인 로직이 복잡하여 인프라 없이 독립 테스트가 필요한 경우

---

## 핵심 개념: 포트와 어댑터

**Port (포트)**: 애플리케이션의 목적 있는 대화(purposeful conversation)를 정의하는 인터페이스. 대부분의 애플리케이션에 최소 2개 이상의 포트가 존재한다.

**Adapter (어댑터)**: 특정 기술을 사용하여 포트와 상호작용하는 구현체. 하나의 포트에 여러 어댑터가 가능하다 (SQL, mock 등).

| 구분 | Driving (Primary) | Driven (Secondary) |
|---|---|---|
| 방향 | 외부 -> 애플리케이션 | 애플리케이션 -> 외부 |
| 역할 | 애플리케이션을 구동 | 애플리케이션이 구동 |
| 예시 | Django View, CLI, Test | DB Adapter, 외부 API, Mock |

---

## 의존성 역전(DIP) 구조

**A.** 고수준 모듈(도메인)이 저수준 모듈(인프라)에 의존해서는 안 된다. 둘 다 추상화에 의존해야 한다.

**B.** 추상화(인터페이스)는 상위/정책 레이어(도메인)가 정의하고 소유하며, 하위 레이어(인프라)가 이를 구현한다 (소유권 역전).

```
[Django View / CLI / Test]     -- Driving Adapter
        |
        v
[Application Service]          -- Use Case 조율
        |
        v
[Port Interface (ABC)]         -- 도메인이 정의하고 소유
        ^
        |
[Infrastructure Adapter]       -- 인프라가 구현
```

---

## Django 프로젝트 구조

Two Scoops 레이아웃을 기반으로 헥사고날 구조를 도입한다. `config/`에 설정, `apps/`에 도메인 앱을 배치한다.

```
repository_root/
    config/
        settings/
            base.py
            local.py
            production.py
            test.py
        urls.py
        wsgi.py
    apps/
        orders/                     # 도메인 앱 (간결한 복수형)
            __init__.py
            domain/                 # 핵심 비즈니스 로직
                models.py           # Django 모델 (도메인 엔티티)
                services.py         # 서비스 함수 (Use Case)
                selectors.py        # 읽기 전용 쿼리 로직
                ports.py            # Driven Port 인터페이스 (ABC)
                exceptions.py       # 도메인 예외
            adapters/               # 인프라 구현
                repositories.py     # Repository 구현 (Django ORM)
                external_api.py     # 외부 API 어댑터
                notification.py     # 알림 어댑터
            api/                    # Driving Adapter (Django Ninja)
                endpoints.py
                schemas.py
            views.py                # Driving Adapter (웹 뷰)
            admin.py
            urls.py
            tests/
                test_services.py
                test_selectors.py
                fakes.py            # Fake Adapter (테스트용)
        payments/
            ...
    manage.py
```

---

## 포트 정의: 도메인 계층이 인터페이스를 소유한다

포트 인터페이스는 기술적 연산이 아닌 **도메인 의도**를 표현해야 한다. 인터페이스는 도메인 계층(`domain/ports.py`)에 위치한다.

```python
# apps/orders/domain/ports.py
from abc import ABC, abstractmethod
from decimal import Decimal


class PaymentGateway(ABC):
    """결제 처리를 위한 Driven Port."""

    @abstractmethod
    def charge(
        self, *, amount: Decimal, currency: str, payment_method_id: str
    ) -> str:
        """결제를 실행하고 트랜잭션 ID를 반환한다."""
        ...

    @abstractmethod
    def refund(self, *, transaction_id: str, amount: Decimal) -> bool:
        """환불을 처리한다."""
        ...


class NotificationSender(ABC):
    """알림 발송을 위한 Driven Port."""

    @abstractmethod
    def send_order_confirmation(self, *, email: str, order_id: int) -> None: ...

    @abstractmethod
    def send_shipping_update(
        self, *, email: str, tracking_number: str
    ) -> None: ...


class InventoryChecker(ABC):
    """재고 확인을 위한 Driven Port."""

    @abstractmethod
    def check_availability(
        self, *, product_id: int, quantity: int
    ) -> bool: ...

    @abstractmethod
    def reserve(self, *, product_id: int, quantity: int) -> str:
        """재고를 예약하고 예약 ID를 반환한다."""
        ...
```

---

## 어댑터 구현: 인프라 계층이 포트를 구현한다

어댑터 구현에 비즈니스 로직이 포함되어서는 안 된다. 어댑터는 순수한 기술적 변환만 담당한다.

```python
# apps/orders/adapters/external_api.py
from decimal import Decimal

import stripe

from apps.orders.domain.ports import PaymentGateway


class StripePaymentGateway(PaymentGateway):
    """Stripe를 사용하는 결제 어댑터."""

    def __init__(self, api_key: str):
        self._api_key = api_key

    def charge(
        self, *, amount: Decimal, currency: str, payment_method_id: str
    ) -> str:
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency=currency,
            payment_method=payment_method_id,
            confirm=True,
            api_key=self._api_key,
        )
        return intent.id

    def refund(self, *, transaction_id: str, amount: Decimal) -> bool:
        stripe.Refund.create(
            payment_intent=transaction_id,
            amount=int(amount * 100),
            api_key=self._api_key,
        )
        return True
```

```python
# apps/orders/adapters/notification.py
from django.core.mail import send_mail

from apps.orders.domain.ports import NotificationSender


class EmailNotificationSender(NotificationSender):
    """이메일 기반 알림 어댑터."""

    def send_order_confirmation(self, *, email: str, order_id: int) -> None:
        send_mail(
            subject=f"주문 #{order_id} 확인",
            message=f"주문 #{order_id}이 확정되었습니다.",
            from_email=None,
            recipient_list=[email],
        )

    def send_shipping_update(
        self, *, email: str, tracking_number: str
    ) -> None:
        send_mail(
            subject="배송 업데이트",
            message=f"송장번호: {tracking_number}",
            from_email=None,
            recipient_list=[email],
        )
```

---

## 서비스 레이어: 포트를 주입받아 유스케이스를 조율한다

서비스 함수는 `<entity>_<action>` 네이밍을 따른다. 포트를 매개변수로 주입받아 의존성 역전을 달성한다. 트랜잭션이 성공적으로 커밋된 후에만 실행되어야 하는 부수 효과(이메일, 알림)에는 `transaction.on_commit()`을 사용한다.

```python
# apps/orders/domain/services.py
from decimal import Decimal

from django.db import transaction

from apps.orders.domain.exceptions import InsufficientInventoryError
from apps.orders.domain.models import Order, OrderItem
from apps.orders.domain.ports import (
    InventoryChecker,
    NotificationSender,
    PaymentGateway,
)


def order_create(
    *,
    user,
    items: list[dict],
    payment_method_id: str,
    payment_gateway: PaymentGateway,
    inventory_checker: InventoryChecker,
    notification_sender: NotificationSender,
) -> Order:
    """주문을 생성하고, 재고를 확인하고, 결제를 처리한다."""
    # 1. 재고 확인
    for item in items:
        if not inventory_checker.check_availability(
            product_id=item["product_id"], quantity=item["quantity"]
        ):
            raise InsufficientInventoryError(
                f"상품 {item['product_id']}의 재고가 부족합니다."
            )

    with transaction.atomic():
        # 2. 주문 생성
        order = Order.objects.create(
            user=user,
            status=Order.Status.PENDING,
        )
        total = Decimal("0")
        for item in items:
            order_item = OrderItem.objects.create(
                order=order,
                product_id=item["product_id"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
            )
            total += order_item.unit_price * order_item.quantity
            inventory_checker.reserve(
                product_id=item["product_id"],
                quantity=item["quantity"],
            )

        # 3. 결제 처리
        transaction_id = payment_gateway.charge(
            amount=total,
            currency="KRW",
            payment_method_id=payment_method_id,
        )
        order.payment_transaction_id = transaction_id
        order.total = total
        order.status = Order.Status.CONFIRMED
        order.save(update_fields=["payment_transaction_id", "total", "status"])

    # 4. 부수 효과는 트랜잭션 커밋 후 실행
    transaction.on_commit(
        lambda: notification_sender.send_order_confirmation(
            email=user.email, order_id=order.pk
        )
    )
    return order
```

---

## 의존성 주입: Django에서의 조립

Django에는 DI 컨테이너가 내장되어 있지 않으므로, 설정 기반으로 구체 어댑터를 조립한다. DIP는 설계 원칙이고, DI는 이를 달성하는 구현 기법이다.

```python
# apps/orders/adapters/dependencies.py
from django.conf import settings

from apps.orders.adapters.external_api import StripePaymentGateway
from apps.orders.adapters.notification import EmailNotificationSender
from apps.orders.adapters.inventory import ExternalInventoryChecker
from apps.orders.domain.ports import (
    InventoryChecker,
    NotificationSender,
    PaymentGateway,
)


def get_payment_gateway() -> PaymentGateway:
    return StripePaymentGateway(api_key=settings.STRIPE_API_KEY)


def get_notification_sender() -> NotificationSender:
    return EmailNotificationSender()


def get_inventory_checker() -> InventoryChecker:
    return ExternalInventoryChecker(base_url=settings.INVENTORY_API_URL)
```

뷰(Driving Adapter)에서 조립하여 서비스에 주입한다:

```python
# apps/orders/views.py
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from apps.orders.adapters.dependencies import (
    get_inventory_checker,
    get_notification_sender,
    get_payment_gateway,
)
from apps.orders.domain.services import order_create


@login_required
def order_create_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        order = order_create(
            user=request.user,
            items=_parse_items(request.POST),
            payment_method_id=request.POST["payment_method_id"],
            payment_gateway=get_payment_gateway(),
            inventory_checker=get_inventory_checker(),
            notification_sender=get_notification_sender(),
        )
        return redirect("order-detail", pk=order.pk)
    # ...
```

---

## 테스트: Fake 어댑터로 인프라 없이 도메인 테스트

헥사고날 아키텍처의 핵심 이점은 테스트 용이성이다. 포트 인터페이스에 대한 Fake 구현으로 인프라 의존 없이 비즈니스 로직을 테스트한다.

```python
# apps/orders/tests/fakes.py
from decimal import Decimal

from apps.orders.domain.ports import (
    InventoryChecker,
    NotificationSender,
    PaymentGateway,
)


class FakePaymentGateway(PaymentGateway):
    def __init__(self):
        self.charges: list[dict] = []

    def charge(
        self, *, amount: Decimal, currency: str, payment_method_id: str
    ) -> str:
        self.charges.append(
            {
                "amount": amount,
                "currency": currency,
                "payment_method_id": payment_method_id,
            }
        )
        return f"fake-txn-{len(self.charges)}"

    def refund(self, *, transaction_id: str, amount: Decimal) -> bool:
        return True


class FakeNotificationSender(NotificationSender):
    def __init__(self):
        self.sent: list[dict] = []

    def send_order_confirmation(self, *, email: str, order_id: int) -> None:
        self.sent.append({"type": "confirmation", "email": email, "order_id": order_id})

    def send_shipping_update(
        self, *, email: str, tracking_number: str
    ) -> None:
        self.sent.append({"type": "shipping", "email": email, "tracking_number": tracking_number})


class FakeInventoryChecker(InventoryChecker):
    def __init__(self, available: bool = True):
        self._available = available
        self.reservations: list[dict] = []

    def check_availability(
        self, *, product_id: int, quantity: int
    ) -> bool:
        return self._available

    def reserve(self, *, product_id: int, quantity: int) -> str:
        self.reservations.append(
            {"product_id": product_id, "quantity": quantity}
        )
        return f"fake-reservation-{len(self.reservations)}"
```

```python
# apps/orders/tests/test_services.py
from decimal import Decimal

from django.test import TestCase

from apps.orders.domain.exceptions import InsufficientInventoryError
from apps.orders.domain.services import order_create
from apps.orders.tests.fakes import (
    FakeInventoryChecker,
    FakeNotificationSender,
    FakePaymentGateway,
)
from apps.users.tests.factories import UserFactory


class OrderCreateTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.payment_gateway = FakePaymentGateway()
        self.notification_sender = FakeNotificationSender()
        self.inventory_checker = FakeInventoryChecker(available=True)
        self.items = [
            {"product_id": 1, "quantity": 2, "unit_price": Decimal("10000")},
        ]

    def test_creates_order_and_charges_payment(self):
        order = order_create(
            user=self.user,
            items=self.items,
            payment_method_id="pm_test",
            payment_gateway=self.payment_gateway,
            inventory_checker=self.inventory_checker,
            notification_sender=self.notification_sender,
        )

        self.assertEqual(order.total, Decimal("20000"))
        self.assertEqual(len(self.payment_gateway.charges), 1)
        self.assertEqual(
            self.payment_gateway.charges[0]["amount"], Decimal("20000")
        )

    def test_raises_error_when_inventory_insufficient(self):
        self.inventory_checker = FakeInventoryChecker(available=False)

        with self.assertRaises(InsufficientInventoryError):
            order_create(
                user=self.user,
                items=self.items,
                payment_method_id="pm_test",
                payment_gateway=self.payment_gateway,
                inventory_checker=self.inventory_checker,
                notification_sender=self.notification_sender,
            )

        self.assertEqual(len(self.payment_gateway.charges), 0)
```

---

## Django ORM과의 트레이드오프

Django ORM은 Active Record 패턴이므로, 완전한 Persistence Ignorance를 달성하기는 어렵다. SQLAlchemy의 classical mapper와 달리 순수 도메인 객체에 매핑하는 메커니즘이 존재하지 않는다.

**실용적 권고:**
- Django 모델을 도메인 엔티티로 직접 사용한다. 별도의 순수 도메인 클래스 + `to_domain()`/`from_domain()` 변환 레이어를 도입하면, Django의 장점(admin, forms, migrations)을 재구현하는 비용이 발생한다.
- Repository 패턴은 선택적으로 도입한다. 대부분의 Django 프로젝트에서는 모델 메서드 + 서비스 함수로 충분하다. 도메인이 정말 복잡해질 때만 점진적으로 도입한다.
- 헥사고날의 핵심 이점인 **외부 시스템 격리**에 집중한다. DB 접근 추상화보다 결제, 알림, 외부 API 등 교체 가능성이 높은 인프라에 포트/어댑터를 우선 적용한다.

```python
# Repository 도입 시 -- 도메인이 정말 복잡한 경우에만
# apps/orders/domain/ports.py
class OrderRepository(ABC):
    @abstractmethod
    def get_by_id(self, order_id: int) -> Order: ...

    @abstractmethod
    def save(self, order: Order) -> None: ...

    @abstractmethod
    def pending_by_user(self, user) -> QuerySet: ...


# apps/orders/adapters/repositories.py
class DjangoOrderRepository(OrderRepository):
    def get_by_id(self, order_id: int) -> Order:
        return Order.objects.select_related("user").get(pk=order_id)

    def save(self, order: Order) -> None:
        order.save()

    def pending_by_user(self, user) -> QuerySet:
        return Order.objects.filter(
            user=user, status=Order.Status.PENDING
        ).select_related("user")
```

---

## 의존성 방향 요약

```
Driving Adapters (외부 -> 안)          Driven Adapters (안 -> 외부)
================================      ================================
Django View                           StripePaymentGateway
Django Ninja Endpoint                 EmailNotificationSender
CLI Command                           ExternalInventoryChecker
Celery Task                           DjangoOrderRepository
Test                                  FakePaymentGateway (테스트용)
        |                                       ^
        v                                       |
  +-----------------------------------------+
  |  Application Service (domain/services.py) |
  |    - 포트 인터페이스에만 의존               |
  |    - 구체 구현을 모름                       |
  +-----------------------------------------+
        |                                       ^
        v                                       |
  +-----------------------------------------+
  |  Port Interface (domain/ports.py)         |
  |    - ABC로 정의                            |
  |    - 도메인 계층이 소유                     |
  +-----------------------------------------+
```

모든 소스 코드 의존성은 안쪽(도메인)을 향한다. 도메인은 인프라를 import하지 않는다. 인프라가 도메인의 포트 인터페이스를 import하여 구현한다.

---

도메인 모델링(애그리거트, 엔티티, 바운디드 컨텍스트)에 대한 상세 가이드는 **architecture-ddd** 스킬을 참조하세요.

CQRS, 이벤트 소싱 등 추가 아키텍처 패턴에 대해서는 **architecture-implementation-patterns** 스킬을 참조하세요.

Django ORM, QuerySet 최적화, 마이그레이션 등 Django 프레임워크 고유 패턴에 대해서는 **implementation-django** 스킬을 참조하세요.

API 엔드포인트(Django Ninja)의 Schema, Router, 인증 패턴에 대해서는 **implementation-django-ninja** 스킬을 참조하세요.

Python 타입 힌트, ABC, 데이터클래스 등 언어 수준 컨벤션에 대해서는 **implementation-python** 스킬을 참조하세요.

REST API 설계 원칙(엔드포인트, 상태 코드, 버저닝)에 대해서는 **architecture-api** 스킬을 참조하세요.

클린 코드 원칙(SOLID, 네이밍)에 대해서는 **implementation-cleancode** 스킬을 참조하세요.
