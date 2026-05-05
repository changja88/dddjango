모델 메서드가 `validation + 외부 API 호출 + 상태 변경 + save`를 모두 한다면, 핵심 문제는 “모델이 도메인 상태의 주인”을 넘어 “애플리케이션 흐름과 인프라 세부사항”까지 떠안고 있다는 점입니다. 리팩터링 방향은 한 번에 전부 분리하기보다 변경 이유 기준으로 나누는 게 좋습니다.

추천 구조는 이렇습니다.

1. **모델에는 도메인 불변식과 상태 전이만 남기기**

모델은 자기 상태가 어떤 조건에서 바뀔 수 있는지, 바뀔 때 어떤 필드가 함께 갱신되어야 하는지를 책임지게 합니다.

```python
class Order(models.Model):
    status = models.CharField(...)
    approved_at = models.DateTimeField(null=True, blank=True)

    def can_approve(self):
        return self.status == OrderStatus.PENDING

    def approve(self, *, approved_at):
        if not self.can_approve():
            raise ValidationError("Only pending orders can be approved.")

        self.status = OrderStatus.APPROVED
        self.approved_at = approved_at
```

여기서 `approve()`는 상태를 바꾸지만 `save()`는 하지 않는 편이 보통 더 명시적입니다. 호출자가 트랜잭션, 저장 시점, 후속 작업을 제어할 수 있기 때문입니다.

2. **외부 API 호출은 모델 밖으로 빼기**

외부 API는 DB 모델의 내부 책임이 아닙니다. HTTP, SDK, 타임아웃, 재시도, 인증, 응답 포맷 변경 같은 이유로 바뀌기 때문입니다.

```python
class PaymentGateway:
    def approve_payment(self, order):
        ...
```

모델이 `requests`, SDK client, settings, env var 등을 직접 알면 테스트도 어려워지고 도메인 코드가 인프라에 묶입니다.

3. **흐름 조율은 서비스/use case 계층으로 옮기기**

검증, 외부 API 호출, 모델 상태 변경, 저장을 하나의 애플리케이션 작업으로 묶는 객체나 함수가 필요합니다.

```python
from django.db import transaction
from django.utils import timezone

class ApproveOrderService:
    def __init__(self, payment_gateway):
        self.payment_gateway = payment_gateway

    @transaction.atomic
    def execute(self, order):
        order.validate_can_approve()

        self.payment_gateway.approve_payment(order)

        order.approve(approved_at=timezone.now())
        order.save(update_fields=["status", "approved_at"])
        return order
```

이렇게 하면 책임이 분명해집니다.

- 모델: “이 상태 전이가 도메인적으로 가능한가?”
- Gateway/API client: “외부 시스템과 어떻게 통신하는가?”
- Service/use case: “이 유스케이스의 순서는 무엇인가?”

4. **validation 종류를 구분하기**

모든 validation을 모델에 넣는 것도 답은 아닙니다.

- 모델에 둘 것: 상태 불변식, 필드 간 규칙, 도메인적으로 항상 참이어야 하는 조건
- 서비스에 둘 것: 특정 유스케이스에서만 필요한 조건
- serializer/form에 둘 것: 입력 형식, 사용자 요청 검증, 화면/API 레벨 메시지
- DB constraint에 둘 것: 유일성, null 여부, 참조 무결성처럼 저장소가 강제해야 하는 규칙

5. **`save()`는 가능한 한 바깥에서 명시적으로 호출하기**

모델 메서드 안에서 `save()`까지 하면 호출자는 메모리 상태 변경인지 DB 반영까지 일어나는지 예측하기 어렵습니다. 특히 테스트, bulk 처리, 트랜잭션 제어, `update_fields` 관리가 불편해집니다.

예외적으로 `order.cancel_and_save()`처럼 이름이 아주 명시적이고 프로젝트 관례가 있다면 유지할 수 있지만, 기본값은 “상태 변경과 저장 분리”가 더 낫습니다.

요약하면, 모델 메서드를 바로 얇게 찢기보다 먼저 다음 형태를 목표로 잡으면 됩니다.

```python
# before
order.approve_with_payment()

# after
approve_order_service.execute(order)
```

그리고 내부는:

```python
order.validate_can_approve()
payment_gateway.approve_payment(order)
order.approve(approved_at=now)
order.save(update_fields=[...])
```

이 방향이 클린 코드 관점에서 가장 무난합니다. 과한 추상화를 피하면서도, 도메인 규칙과 외부 API 세부사항, 저장 흐름의 변경 이유를 분리할 수 있습니다.