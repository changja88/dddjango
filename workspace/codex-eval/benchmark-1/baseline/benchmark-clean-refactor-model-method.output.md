Django model method에 `validation`, 외부 API 호출, 상태 변경, `save()`가 섞여 있다면 핵심 문제는 **도메인 객체가 너무 많은 책임을 갖고 있고, I/O와 상태 전이가 강하게 결합되어 있다는 점**입니다. 리팩터링 방향은 다음이 좋습니다.

**권장 구조**

모델은 가능한 한 다음 정도만 책임지게 두세요.

```python
class Order(models.Model):
    status = models.CharField(...)

    def can_cancel(self):
        return self.status in ["pending", "paid"]

    def mark_cancelled(self):
        if not self.can_cancel():
            raise ValidationError("Cannot cancel order")
        self.status = "cancelled"
```

외부 API 호출과 저장 흐름은 별도 서비스로 뺍니다.

```python
class CancelOrderService:
    def __init__(self, payment_client):
        self.payment_client = payment_client

    def execute(self, order):
        if not order.can_cancel():
            raise ValidationError("Cannot cancel order")

        self.payment_client.cancel(order.payment_id)

        order.mark_cancelled()
        order.save(update_fields=["status"])
```

**분리 기준**

- `validation`: 모델의 불변 조건이면 모델 메서드나 `clean()`에 둡니다. 유스케이스별 검증이면 서비스 계층으로 뺍니다.
- 외부 API 호출: 모델에서 제거하고 `client`, `gateway`, `adapter` 같은 별도 객체로 분리합니다.
- 상태 변경: 모델 메서드에 남겨도 됩니다. 단, DB 저장은 하지 않고 메모리 상태만 바꾸는 형태가 깔끔합니다.
- `save()`: 서비스나 애플리케이션 계층에서 호출하게 둡니다. 모델 메서드 안에서 몰래 저장하면 테스트와 트랜잭션 제어가 어려워집니다.

**트랜잭션 주의점**

외부 API 호출과 DB 저장을 한 트랜잭션 안에 무심코 넣으면 위험합니다.

```python
with transaction.atomic():
    external_api.call()
    model.save()
```

이 구조는 DB 롤백과 외부 API 롤백이 맞지 않을 수 있습니다. 보통은 다음 중 하나를 선택합니다.

- 외부 API 성공 후 DB 상태 변경
- DB에 “요청 중” 상태 저장 후 비동기 작업에서 외부 API 호출
- `transaction.on_commit()`으로 커밋 이후 외부 호출
- 멱등성 키를 사용해 재시도 가능하게 설계

**최종 방향**

모델 메서드는 “이 상태 전이가 가능한가?”와 “상태를 어떻게 바꾸는가?”에 집중시키고, 실제 유스케이스 흐름은 서비스 객체로 옮기는 게 좋습니다. 외부 API는 어댑터로 감싸서 테스트에서는 mock/fake로 대체할 수 있게 만들면 클린 코드 관점에서도 책임 분리가 선명해지고, 장애 처리와 재시도 정책도 훨씬 다루기 쉬워집니다.