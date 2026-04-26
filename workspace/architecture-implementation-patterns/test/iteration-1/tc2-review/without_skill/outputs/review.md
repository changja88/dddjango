# Architecture Review: OrderService.confirm_order

## 1. 요약

`OrderService.confirm_order` 메서드는 주문 확인에 필요한 모든 작업(DB 조회, 결제, 상태 변경, 이메일 발송, 외부 시스템 호출, 응답 구성)을 하나의 메서드 안에서 순차적으로 처리하고 있다. 도메인 서비스라는 이름과 달리 인프라스트럭처 의존성이 직접 주입되어 있어, 테스트가 어렵고 변경에 취약한 구조이다.

---

## 2. 식별된 문제

### 2.1 도메인 레이어가 인프라스트럭처에 직접 의존

**위치:** `order/domain/order_service.py`

도메인 서비스가 `order.infrastructure.models`, `order.infrastructure.email_client`, `requests`, `stripe`를 직접 import하고 있다. 클린 아키텍처 / 헥사고날 아키텍처에서 도메인 레이어는 어떤 인프라스트럭처에도 의존해서는 안 된다. 의존성 방향이 역전되어 있다.

```
현재: domain -> infrastructure (위반)
올바른 방향: infrastructure -> domain
```

### 2.2 단일 책임 원칙(SRP) 위반

`confirm_order` 메서드 하나가 5가지 책임을 동시에 수행한다:

| # | 책임 | 관심사 |
|---|------|--------|
| 1 | 주문 조회 | 데이터 접근 |
| 2 | 결제 처리 | 외부 결제 게이트웨이 |
| 3 | 상태 변경 및 저장 | 도메인 로직 + 영속화 |
| 4 | 이메일 발송 | 알림 |
| 5 | 배송 시스템 알림 | 외부 서비스 연동 |

이 중 어느 하나가 변경되면 이 메서드 전체를 수정해야 한다.

### 2.3 API 키 하드코딩

```python
stripe = Stripe(api_key="sk_live_xxx")
```

프로덕션 시크릿이 소스 코드에 직접 노출되어 있다. 이것은 보안 취약점이며, 키 로테이션 시 코드를 다시 배포해야 한다.

### 2.4 트랜잭션 경계 부재

결제는 성공했는데 `order.save()`가 실패하거나, 저장은 성공했는데 이메일 발송에서 예외가 발생하는 경우에 대한 처리가 없다. 부분 실패 시 시스템이 일관성 없는 상태에 빠질 수 있다.

- 결제 성공 + DB 저장 실패 = 돈은 빠졌으나 주문은 미확인
- DB 저장 성공 + 이메일 실패 = 예외 전파로 인해 호출자에게 실패로 보고될 수 있음

### 2.5 외부 서비스 호출의 동기적 결합

이메일 발송과 배송 시스템 알림이 주문 확인의 핵심 흐름에 동기적으로 결합되어 있다. 배송 서비스가 응답하지 않으면 (timeout=5초) 주문 확인 자체가 실패한다. 이메일 서버 장애 역시 동일한 문제를 일으킨다.

### 2.6 외부 서비스 URL 하드코딩

```python
requests.post("http://shipping-service/api/shipments", ...)
```

배송 서비스의 URL이 코드에 하드코딩되어 있어 환경별 배포(개발/스테이징/프로덕션)에 대응할 수 없다.

### 2.7 에러 핸들링 부재

어떤 단계에서든 예외가 발생하면 전체 메서드가 실패한다. 복구 로직, 보상 트랜잭션(compensating transaction), 재시도 메커니즘이 없다.

### 2.8 테스트 불가능한 구조

모든 의존성이 메서드 내부에서 직접 생성되거나 모듈 수준에서 import되어 있어, 단위 테스트 시 실제 Stripe API를 호출하거나, 실제 DB에 접근하거나, 실제 HTTP 요청을 보내야 한다. mock/stub으로 대체하려면 monkey-patching이 필요하다.

---

## 3. 개선 방향

### 3.1 의존성 역전 적용

도메인 레이어에 인터페이스(Port)를 정의하고, 인프라스트럭처 레이어에서 구현(Adapter)을 제공하는 구조로 전환한다.

```python
# order/domain/ports.py
from abc import ABC, abstractmethod

class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount: int, currency: str, source: str) -> str: ...

class OrderRepository(ABC):
    @abstractmethod
    def get_by_id(self, order_id: int) -> "Order": ...

    @abstractmethod
    def save(self, order: "Order") -> None: ...

class NotificationService(ABC):
    @abstractmethod
    def send_order_confirmation(self, email: str, order_number: str) -> None: ...

class ShippingService(ABC):
    @abstractmethod
    def request_shipment(self, order_id: int, address: str) -> None: ...
```

### 3.2 도메인 서비스 재설계

```python
# order/domain/order_service.py
class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        payment_gateway: PaymentGateway,
    ):
        self._order_repo = order_repo
        self._payment_gateway = payment_gateway

    def confirm_order(self, order_id: int) -> Order:
        order = self._order_repo.get_by_id(order_id)
        payment_id = self._payment_gateway.charge(
            amount=order.total_amount,
            currency="krw",
            source=order.payment_token,
        )
        order.confirm(payment_id)
        self._order_repo.save(order)
        return order
```

핵심 비즈니스 로직(결제 + 상태 확인)만 도메인 서비스에 남기고, 부수 효과(이메일, 배송 알림)는 도메인 이벤트로 분리한다.

### 3.3 도메인 이벤트를 통한 부수 효과 분리

```python
# order/domain/events.py
@dataclass(frozen=True)
class OrderConfirmed:
    order_id: int
    user_email: str
    order_number: str
    shipping_address: str
```

`Order.confirm()` 시점에 `OrderConfirmed` 이벤트를 발행하고, 이메일 발송과 배송 알림은 이벤트 핸들러에서 비동기로 처리한다. 이렇게 하면 이메일/배송 서비스 장애가 주문 확인 흐름에 영향을 주지 않는다.

### 3.4 트랜잭션 관리

결제와 DB 저장을 하나의 트랜잭션 단위로 묶되, 결제 실패 시 DB 변경이 롤백되도록 구성한다. Django라면 `transaction.atomic()`을 활용할 수 있다. 단, 결제 성공 후 DB 저장 실패 시를 대비한 결제 취소(보상 트랜잭션) 로직도 필요하다.

### 3.5 설정 외부화

API 키, 서비스 URL 등은 환경 변수나 설정 파일에서 주입받도록 변경한다.

---

## 4. 문제 심각도 분류

| 심각도 | 문제 | 이유 |
|--------|------|------|
| Critical | API 키 하드코딩 | 보안 취약점, 즉시 수정 필요 |
| Critical | 트랜잭션 경계 부재 | 데이터 정합성 깨질 수 있음 |
| High | 도메인-인프라 의존성 역전 | 아키텍처 근본 구조 문제 |
| High | SRP 위반 | 변경 영향 범위가 넓음 |
| High | 동기적 외부 서비스 결합 | 가용성에 직접 영향 |
| Medium | 에러 핸들링 부재 | 장애 복구 불가 |
| Medium | URL 하드코딩 | 배포 유연성 저하 |
| Medium | 테스트 불가능한 구조 | 품질 보증 어려움 |
