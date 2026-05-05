지정된 fixture path `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고, 평가 케이스상 `Fixture: none`으로 확인됩니다. 따라서 실제 파일 diff 대신 리팩터링 방향을 리뷰 형식으로 제안합니다.

**핵심 문제**

Django model method가 `validation -> 외부 API 호출 -> 상태 변경 -> save()`를 모두 처리하면 변경 이유가 섞입니다. 특히 외부 API와 DB 저장이 한 메서드에 있으면 테스트가 어려워지고, DB 트랜잭션 롤백과 외부 부수 효과의 정합성도 깨지기 쉽습니다.

**권장 분리**

| 책임 | 위치 |
|---|---|
| 요청 형식 검증 | Form, Django Ninja Schema, View/API layer |
| 도메인 불변식 검증 | model `clean()` 또는 상태 전이 메서드 |
| 상태 변경 | model method |
| 유스케이스 조율 | `services.py` 또는 application service |
| 외부 API 호출 | gateway/client로 분리 후 service에서 호출 |
| 저장 | service에서 `save(update_fields=...)` |
| 커밋 후 부수 효과 | `transaction.on_commit()` 또는 outbox |

예시 방향은 이렇게 잡는 편이 좋습니다.

```python
# models.py
class Order(models.Model):
    status = models.CharField(max_length=20)

    def approve(self) -> None:
        if self.status != OrderStatus.PENDING:
            raise OrderCannotBeApproved()
        self.status = OrderStatus.APPROVED
```

```python
# services.py
from django.db import transaction

def approve_order(*, order_id: int, payment_gateway) -> Order:
    with transaction.atomic():
        order = Order.objects.select_for_update().get(id=order_id)

        payment_gateway.authorize(order.payment_reference)

        order.approve()
        order.full_clean()
        order.save(update_fields=["status"])

    return order
```

외부 API 호출이 “DB 변경 후에만 실행되어야 하는 알림/웹훅” 성격이면 트랜잭션 안에서 바로 호출하지 말고:

```python
transaction.on_commit(lambda: notifier.send_order_approved(order.id))
```

처럼 커밋 이후로 미루는 게 안전합니다. 반대로 결제 승인처럼 상태 변경 전에 성공해야 하는 호출은 service 계층에서 명시적으로 호출하되, 실패 시 DB 상태가 바뀌지 않도록 트랜잭션 경계를 분명히 둡니다.

테스트는 모델 단위에서 상태 전이 규칙을 검증하고, service 단위에서 fake gateway를 주입해 “외부 API 성공/실패”, “상태 저장 여부”, “잘못된 상태에서 예외”를 분리해서 검증하는 방향이 좋습니다.