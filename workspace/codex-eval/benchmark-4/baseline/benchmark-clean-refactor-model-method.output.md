Django 모델 메서드 안에 `validation`, 외부 API 호출, 상태 변경, `save()`가 섞여 있다면 핵심 문제는 **도메인 상태 전이와 I/O가 한 함수에 결합된 것**입니다. 클린 코드 관점에서는 책임을 아래처럼 나누는 방향이 좋습니다.

**권장 구조**

1. **모델은 상태와 불변식 중심으로 유지**
   - 필드, 관계, 간단한 도메인 규칙
   - 순수한 상태 변경 메서드
   - 외부 API 호출이나 복잡한 orchestration은 넣지 않기

```python
class Order(models.Model):
    status = models.CharField(...)

    def mark_paid(self):
        if self.status != OrderStatus.PENDING:
            raise InvalidOrderState("Only pending orders can be paid")
        self.status = OrderStatus.PAID
```

2. **validation은 명시적으로 분리**
   - 필드/모델 수준 검증은 `clean()`, serializer/form validation
   - 유스케이스 검증은 service나 validator 객체
   - 상태 전이 검증은 모델 메서드에 남겨도 괜찮음

```python
class OrderPaymentValidator:
    def validate(self, order):
        if order.is_expired:
            raise ValidationError("Expired order")
```

3. **외부 API 호출은 client/gateway로 분리**
   - 결제사, 배송사, CRM 등 외부 시스템 호출은 `PaymentClient`, `ShippingGateway` 같은 객체로 격리
   - 모델이 `requests.post()`를 직접 호출하지 않게 하기
   - 테스트에서 mock/stub 하기 쉬워짐

```python
class PaymentClient:
    def charge(self, order):
        ...
```

4. **전체 흐름은 application service/use case에서 조립**
   - validation
   - 외부 API 호출
   - 모델 상태 변경
   - transaction
   - save
   - 후속 작업 enqueue

```python
class PayOrderService:
    def __init__(self, payment_client):
        self.payment_client = payment_client

    @transaction.atomic
    def execute(self, order):
        OrderPaymentValidator().validate(order)

        result = self.payment_client.charge(order)

        order.mark_paid()
        order.payment_id = result.payment_id
        order.save(update_fields=["status", "payment_id", "updated_at"])

        return order
```

5. **트랜잭션과 외부 API 호출 순서를 신중히 결정**
   - DB transaction 안에서 외부 API를 오래 기다리는 것은 위험할 수 있음
   - 보통은 다음 중 하나를 선택합니다:
     - API 호출 성공 후 짧은 transaction으로 상태 저장
     - 먼저 `PROCESSING` 저장 후 API 호출, 결과에 따라 `SUCCESS/FAILED`
     - Celery 같은 비동기 작업 + idempotency key 사용

**판단 기준**

모델 메서드에 남겨도 되는 것:
- 상태 전이 규칙
- 계산된 속성
- 단순한 도메인 불변식
- DB 저장 없이 객체 상태만 바꾸는 메서드

모델 밖으로 빼는 것이 좋은 것:
- 외부 API 호출
- 이메일/알림 발송
- Celery enqueue
- 여러 모델을 조율하는 흐름
- `transaction.atomic()`이 필요한 유스케이스
- 복잡한 validation과 저장 정책

결론적으로는 **모델은 “상태를 어떻게 바꿀 수 있는가”를 알고, service는 “언제 무엇을 호출하고 저장할 것인가”를 책임지게 하는 방향**이 가장 무난합니다. 이렇게 나누면 테스트도 `모델 단위 테스트`, `API client 테스트`, `service orchestration 테스트`로 깔끔하게 분리됩니다.