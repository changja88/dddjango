모델 메서드 안에 `validation`, 외부 API 호출, 상태 변경, `save()`가 섞여 있다면 핵심 문제는 “도메인 객체가 너무 많은 책임을 가진다”는 점입니다. Django에서는 보통 아래 방향으로 분리하는 게 깔끔합니다.

**권장 리팩터링 방향**

1. **Model은 상태와 도메인 규칙만 남기기**

모델 메서드는 가능하면 순수한 상태 전이 정도만 담당하게 둡니다.

```python
class Order(models.Model):
    status = models.CharField(...)

    def mark_paid(self):
        if self.status != OrderStatus.PENDING:
            raise InvalidOrderState()
        self.status = OrderStatus.PAID
```

여기서는 외부 API 호출도, `save()`도 하지 않는 편이 좋습니다.

2. **Validation은 명시적인 계층으로 분리**

입력값 검증은 상황에 따라 위치를 나눕니다.

- 폼/요청 데이터 검증: `Form`, `Serializer`, `Pydantic`, DTO
- DB 무결성: model field, constraint, `clean()`
- 비즈니스 규칙 검증: domain service 또는 model method

예를 들어 “결제 가능한 주문인가?”는 모델이나 도메인 서비스에 두고, “카드 번호 형식이 맞는가?”는 입력 계층에 두는 식입니다.

3. **외부 API 호출은 Service 또는 Gateway로 분리**

모델에서 직접 `requests.post(...)` 같은 호출을 하지 말고, 외부 시스템 접근을 별도 객체로 빼는 게 좋습니다.

```python
class PaymentGateway:
    def charge(self, order, payment_method):
        ...
```

그리고 비즈니스 흐름은 application service가 조율합니다.

```python
class PayOrderService:
    def __init__(self, payment_gateway):
        self.payment_gateway = payment_gateway

    def execute(self, order, payment_method):
        order.validate_payable()

        result = self.payment_gateway.charge(order, payment_method)

        order.mark_paid()
        order.payment_id = result.payment_id
        order.save(update_fields=["status", "payment_id"])
```

4. **상태 변경과 저장 시점을 명확히 하기**

모델 메서드가 내부에서 `save()`까지 해버리면 테스트와 트랜잭션 제어가 어려워집니다. 보통은 둘 중 하나로 통일합니다.

```python
order.mark_paid()
order.save()
```

또는 서비스 계층에서만 저장합니다.

```python
PayOrderService(...).execute(order, payment_method)
```

후자가 외부 API, 트랜잭션, 상태 변경이 엮인 경우 더 낫습니다.

5. **트랜잭션 경계는 Service에 둔다**

외부 API 호출과 DB 저장이 섞이면 실패 시나리오가 중요합니다. `transaction.atomic()`은 모델 메서드보다 서비스 계층에 두는 편이 자연스럽습니다.

```python
from django.db import transaction

class PayOrderService:
    def execute(self, order, payment_method):
        order.validate_payable()

        payment = self.payment_gateway.charge(order, payment_method)

        with transaction.atomic():
            order.mark_paid()
            order.payment_id = payment.id
            order.save(update_fields=["status", "payment_id"])
```

단, 외부 API 호출을 트랜잭션 안에 넣을지는 신중해야 합니다. DB 락 시간이 길어질 수 있어서 보통은 피합니다.

**실용적인 구조 예시**

```text
orders/
  models.py              # Order 상태, 핵심 도메인 규칙
  services.py            # PayOrderService 같은 유스케이스 조율
  gateways.py            # 외부 결제 API 어댑터
  exceptions.py          # InvalidOrderState 등
  tests/
    test_order_model.py
    test_pay_order_service.py
```

**정리하면**

모델 메서드에는 “이 객체가 어떤 상태로 바뀔 수 있는가”만 남기고, 외부 API 호출과 저장 흐름은 service 계층으로 올리는 방향이 좋습니다. 그러면 테스트가 쉬워지고, 실패 처리, 재시도, 트랜잭션 경계도 훨씬 명확해집니다.