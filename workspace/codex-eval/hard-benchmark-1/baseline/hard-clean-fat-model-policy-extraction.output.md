Django `Order` fat model을 줄일 때 핵심은 “도메인 상태 전이”와 “외부 작업”을 분리하는 것입니다.

`cancel`, `refund`, `calculate_fee`, `notify`, `call_pg`가 한 모델에 있으면 보통 다음 관심사가 섞여 있습니다.

- 주문 도메인 규칙: 취소 가능 여부, 환불 가능 여부, 상태 변경
- 정책 계산: 취소 수수료, 환불 금액
- 외부 I/O: PG 호출, 알림 발송
- 애플리케이션 흐름: 트랜잭션, 저장, 실패 처리, 순서 제어

## Before

```python
# orders/models.py

class Order(models.Model):
    status = models.CharField(...)
    paid_amount = models.PositiveIntegerField(...)
    canceled_at = models.DateTimeField(null=True)
    refunded_amount = models.PositiveIntegerField(default=0)

    def cancel(self, reason):
        if self.status != "PAID":
            raise ValueError("취소할 수 없는 주문입니다.")

        fee = self.calculate_fee()

        pg_result = self.call_pg(
            amount=self.paid_amount - fee,
            reason=reason,
        )

        if not pg_result.success:
            raise ValueError("PG 취소 실패")

        self.status = "CANCELED"
        self.canceled_at = timezone.now()
        self.refunded_amount = self.paid_amount - fee
        self.save()

        self.notify()

    def refund(self, amount):
        if self.status not in ["PAID", "PARTIAL_REFUNDED"]:
            raise ValueError("환불할 수 없는 주문입니다.")

        pg_result = self.call_pg(amount=amount)

        if not pg_result.success:
            raise ValueError("PG 환불 실패")

        self.refunded_amount += amount
        self.status = "REFUNDED"
        self.save()

        self.notify()

    def calculate_fee(self):
        # 날짜, 상품, 쿠폰, 정책 조건이 뒤섞임
        ...

    def call_pg(self, amount, reason=None):
        # PG SDK 직접 호출
        ...

    def notify(self):
        # SMS, Email, 알림톡 등 직접 호출
        ...
```

문제는 `Order`가 너무 많은 변경 이유를 가진다는 점입니다.

- 취소 정책이 바뀌어도 `Order` 수정
- PG사가 바뀌어도 `Order` 수정
- 알림 문구가 바뀌어도 `Order` 수정
- 트랜잭션 흐름이 바뀌어도 `Order` 수정

## After 구조

추천 구조는 다음처럼 나눕니다.

```text
orders/
  models.py
  services/
    cancel_order.py
    refund_order.py
  policies/
    cancellation_fee_policy.py
    refund_policy.py
  gateways/
    payment_gateway.py
  notifications/
    order_notifier.py
  tests/
    test_order_model.py
    test_cancel_order_service.py
    test_refund_order_service.py
    test_cancellation_fee_policy.py
```

## 1. Order 모델은 상태와 불변식 중심으로 축소

```python
# orders/models.py

class Order(models.Model):
    status = models.CharField(...)
    paid_amount = models.PositiveIntegerField(...)
    canceled_at = models.DateTimeField(null=True)
    refunded_amount = models.PositiveIntegerField(default=0)

    def can_cancel(self):
        return self.status == OrderStatus.PAID

    def mark_canceled(self, refunded_amount, canceled_at):
        if not self.can_cancel():
            raise OrderCannotBeCanceled()

        self.status = OrderStatus.CANCELED
        self.refunded_amount = refunded_amount
        self.canceled_at = canceled_at

    def can_refund(self):
        return self.status in [
            OrderStatus.PAID,
            OrderStatus.PARTIAL_REFUNDED,
        ]

    def apply_refund(self, amount):
        if not self.can_refund():
            raise OrderCannotBeRefunded()

        if self.refunded_amount + amount > self.paid_amount:
            raise RefundAmountExceeded()

        self.refunded_amount += amount

        if self.refunded_amount == self.paid_amount:
            self.status = OrderStatus.REFUNDED
        else:
            self.status = OrderStatus.PARTIAL_REFUNDED
```

여기서 `Order`는 외부 시스템을 모릅니다.

`Order`가 책임지는 것:

- 현재 상태에서 취소 가능한가
- 환불 금액이 결제 금액을 넘지 않는가
- 취소/환불 후 상태가 무엇인가
- 자신의 불변식을 깨지 않도록 상태 변경

`Order`가 책임지지 않는 것:

- PG 호출
- 알림 발송
- 수수료 정책 세부 계산
- 트랜잭션 흐름
- 저장소 조회 흐름

## 2. 정책 객체는 계산 규칙만 담당

```python
# orders/policies/cancellation_fee_policy.py

class CancellationFeePolicy:
    def calculate(self, order):
        if order.is_same_day_purchase():
            return 0

        if order.used_coupon:
            return 1000

        return 3000
```

정책 객체는 가능하면 순수 함수처럼 유지하는 게 좋습니다.

좋은 정책 객체의 특징:

- DB 저장을 하지 않음
- PG나 알림을 호출하지 않음
- 입력이 같으면 결과가 같음
- 날짜 기준이 필요하면 `now`를 인자로 받거나 clock 객체를 주입함

예를 들어 날짜 의존성이 있으면 이렇게 합니다.

```python
class CancellationFeePolicy:
    def calculate(self, order, now):
        if order.paid_at.date() == now.date():
            return 0

        return 3000
```

## 3. Application Service는 흐름을 조율

```python
# orders/services/cancel_order.py

from django.db import transaction
from django.utils import timezone

class CancelOrderService:
    def __init__(self, fee_policy, payment_gateway, notifier):
        self.fee_policy = fee_policy
        self.payment_gateway = payment_gateway
        self.notifier = notifier

    @transaction.atomic
    def cancel(self, order_id, reason):
        order = (
            Order.objects
            .select_for_update()
            .get(id=order_id)
        )

        fee = self.fee_policy.calculate(order, now=timezone.now())
        refund_amount = order.paid_amount - fee

        self.payment_gateway.cancel(
            payment_key=order.payment_key,
            amount=refund_amount,
            reason=reason,
        )

        order.mark_canceled(
            refunded_amount=refund_amount,
            canceled_at=timezone.now(),
        )
        order.save(update_fields=[
            "status",
            "refunded_amount",
            "canceled_at",
        ])

        self.notifier.order_canceled(order)

        return order
```

Application Service의 책임:

- 주문 조회
- 트랜잭션 경계
- lock 여부 결정
- 정책 객체 호출
- PG gateway 호출
- 모델 상태 변경
- 저장
- 알림 호출

즉, “업무 유스케이스의 순서”를 담습니다.

## 4. PG와 알림은 경계 객체로 분리

```python
# orders/gateways/payment_gateway.py

class PaymentGateway:
    def cancel(self, payment_key, amount, reason):
        raise NotImplementedError
```

```python
class TossPaymentGateway(PaymentGateway):
    def __init__(self, client):
        self.client = client

    def cancel(self, payment_key, amount, reason):
        response = self.client.cancel_payment(
            payment_key=payment_key,
            amount=amount,
            reason=reason,
        )

        if not response.success:
            raise PaymentCancelFailed(response.message)
```

```python
# orders/notifications/order_notifier.py

class OrderNotifier:
    def order_canceled(self, order):
        ...
```

이렇게 하면 `Order`와 application service는 특정 PG SDK, SMS SDK, 이메일 API를 직접 알 필요가 없습니다.

## 테스트 방향

테스트는 책임 단위별로 나눕니다.

### 1. Order 모델 테스트

외부 I/O 없이 상태 전이와 불변식만 검증합니다.

```python
def test_paid_order_can_be_canceled():
    order = Order(status=OrderStatus.PAID, paid_amount=10000)

    order.mark_canceled(refunded_amount=9000, canceled_at=now)

    assert order.status == OrderStatus.CANCELED
    assert order.refunded_amount == 9000
```

검증할 것:

- 결제 완료 주문은 취소 가능
- 이미 취소된 주문은 취소 불가
- 환불 금액이 결제 금액을 넘으면 실패
- 부분 환불과 전체 환불 상태가 올바르게 바뀜

### 2. Policy 테스트

계산 규칙만 촘촘히 봅니다.

```python
def test_same_day_cancel_has_no_fee():
    policy = CancellationFeePolicy()
    order = make_order(paid_at=datetime(2026, 5, 5, 10, 0))

    fee = policy.calculate(order, now=datetime(2026, 5, 5, 15, 0))

    assert fee == 0
```

검증할 것:

- 당일 취소 수수료
- 기간별 수수료
- 쿠폰 사용 여부
- 상품 유형별 예외
- 경계 날짜

### 3. Application Service 테스트

mock/fake gateway, notifier를 사용해서 흐름을 검증합니다.

```python
def test_cancel_order_calls_pg_marks_order_and_sends_notification(db):
    gateway = FakePaymentGateway()
    notifier = FakeOrderNotifier()
    service = CancelOrderService(
        fee_policy=FixedFeePolicy(fee=1000),
        payment_gateway=gateway,
        notifier=notifier,
    )

    order = Order.objects.create(
        status=OrderStatus.PAID,
        paid_amount=10000,
        payment_key="pay_123",
    )

    service.cancel(order.id, reason="customer request")

    order.refresh_from_db()

    assert gateway.cancel_called_with.amount == 9000
    assert order.status == OrderStatus.CANCELED
    assert order.refunded_amount == 9000
    assert notifier.canceled_orders == [order.id]
```

검증할 것:

- 수수료 정책 결과로 환불 금액을 계산하는가
- PG 취소를 호출하는가
- PG 실패 시 주문 상태가 바뀌지 않는가
- 성공 시 주문 상태가 저장되는가
- 알림이 발송되는가
- 동시성 이슈가 있으면 `select_for_update`를 사용하는가

### 4. Gateway 테스트

실제 SDK나 HTTP 호출은 별도 통합 테스트로 얇게 둡니다.

검증할 것:

- 외부 API 요청 payload
- 실패 응답을 도메인 예외로 변환
- timeout, 인증 실패, 중복 취소 응답 처리

## 판단 기준

이 리팩터링에서 가장 중요한 기준은 “메서드를 어디로 옮길까”가 아니라 “변경 이유가 무엇인가”입니다.

- `calculate_fee`는 정책 변경 때문에 바뀌므로 policy
- `call_pg`는 외부 결제 연동 변경 때문에 바뀌므로 gateway
- `notify`는 알림 채널/문구 변경 때문에 바뀌므로 notifier
- `cancel`, `refund`의 전체 흐름은 유스케이스 변경 때문에 바뀌므로 application service
- `Order`는 주문 상태와 불변식 변경 때문에만 바뀌게 유지

처음부터 과한 인터페이스 계층을 만들 필요는 없습니다. 우선 `CancelOrderService`, `RefundOrderService`, `CancellationFeePolicy`, `PaymentGateway`, `OrderNotifier` 정도로 나누고, 실제 변경 축이 반복될 때 정책 객체나 gateway 구현을 더 세분화하는 편이 낫습니다.