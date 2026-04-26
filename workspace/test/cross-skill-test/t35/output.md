# T35 (Test 34): SOLID 위반 God Class가 테스트를 어렵게 만드는 설계 원칙

**Skill:** implementation-test (Writing mode)
**Cross-skill references loaded:** implementation-cleancode (SOLID, God Class), implementation-tdd (테스트 품질)

## [주요 내용]

### God Class가 테스트에 미치는 영향

God Class(단일 책임 원칙 SRP 위반)는 과도한 설정(Excessive Setup) 안티패턴을 유발한다. 하나의 동작을 테스트하기 위해 수십 개의 의존성을 설정해야 한다.

### 문제: 테스트 불가능한 God Class

```python
class OrderManager:
    """God Class -- 주문, 결제, 배송, 알림을 모두 처리"""
    def __init__(self, db, payment_gateway, shipping_api, email_service, sms_service):
        self.db = db
        self.payment = payment_gateway
        self.shipping = shipping_api
        self.email = email_service
        self.sms = sms_service

    def process_order(self, order_data):
        # 100줄의 복합 로직...
        pass
```

```python
# 테스트: 5개 의존성 Mock 필요 -- Excessive Setup 안티패턴
def test_process_order():
    db = Mock()
    payment = Mock()
    shipping = Mock()
    email = Mock()
    sms = Mock()
    manager = OrderManager(db, payment, shipping, email, sms)
    # 테스트 의도가 설정에 묻힌다
```

### 해결: SRP 적용 후 격리된 테스트 (implementation-cleancode 위임)

```python
from typing import Protocol

class PaymentProcessor(Protocol):
    def charge(self, amount: int) -> bool: ...

class OrderService:
    """단일 책임: 주문 처리만 담당"""
    def __init__(self, payment: PaymentProcessor):
        self._payment = payment

    def place_order(self, order: Order) -> bool:
        return self._payment.charge(order.total)
```

```python
# 테스트: 1개 의존성만 필요 -- 의도가 명확하다
def test_place_order_charges_payment():
    payment = Mock(spec=PaymentProcessor)
    payment.charge.return_value = True
    service = OrderService(payment)

    result = service.place_order(OrderFactory(total=5000))

    assert result is True
    payment.charge.assert_called_once_with(5000)
```

### SOLID 원칙과 테스트 품질의 관계 (implementation-tdd 위임)

| SOLID 원칙 | 위반 시 테스트 영향 |
|-----------|-------------------|
| SRP | Excessive Setup, 테스트당 Mock 과다 |
| OCP | 기존 테스트가 새 기능 추가 시 깨짐 |
| LSP | Mock이 실제 동작과 불일치 |
| ISP | 불필요한 메서드까지 Mock 필요 |
| DIP | 구현에 결합된 테스트 (The Inspector) |

---
> **관련 스킬 참조:**
> - [SOLID, SRP, God Class 분리] → **implementation-cleancode** 스킬
> - [테스트 냄새, Excessive Setup] → **implementation-tdd** 스킬
> - [Mock spec, create_autospec] → 이 스킬 `references/mock-patterns.md`
