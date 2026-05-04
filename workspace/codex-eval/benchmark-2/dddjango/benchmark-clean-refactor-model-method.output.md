**[주요 내용]**

현재 모델 메서드는 네 가지 책임이 한곳에 섞여 있습니다.

| 책임 | 둘 위치 |
|---|---|
| 입력/API 요청 형식 검증 | Form/Schema/Application Service |
| 순수 도메인 규칙 검증 | Model 또는 Value Object |
| 외부 API 호출 | Adapter/Gateway |
| 상태 변경 + 저장 트랜잭션 | Application Service |

핵심 방향은 **모델 메서드를 “순수 도메인 규칙 + 상태 전이”만 수행하게 만드는 것**입니다. 모델 안에서 외부 API를 호출하거나 `save()`까지 하면 테스트가 어려워지고, 트랜잭션 실패 후 외부 호출만 성공하는 불일치가 생깁니다.

[Before]

```python
class Order(models.Model):
    def approve(self):
        if self.status != self.Status.PENDING:
            raise ValueError("cannot approve")

        result = external_client.approve(self.external_id)

        if not result.ok:
            raise ValueError("approval failed")

        self.status = self.Status.APPROVED
        self.approved_at = timezone.now()
        self.save()
```

[After]

```python
class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"

    def approve(self, approved_at):
        if self.status != self.Status.PENDING:
            raise OrderCannotBeApproved

        self.status = self.Status.APPROVED
        self.approved_at = approved_at
```

```python
class ApprovalGateway(Protocol):
    def approve(self, external_id: str) -> None: ...


@transaction.atomic
def approve_order(order_id: int, gateway: ApprovalGateway) -> None:
    order = Order.objects.select_for_update().get(id=order_id)

    gateway.approve(order.external_id)

    order.approve(approved_at=timezone.now())
    order.save(update_fields=["status", "approved_at"])
```

[Reason] Clean Code / DDD -- 모델은 “주문이 승인될 수 있는가”와 “승인되면 어떤 상태가 되는가”만 책임집니다. 외부 API 호출과 DB 저장은 유스케이스를 조율하는 Application Service가 담당합니다.

다만 외부 API 호출이 DB 커밋 이후에 실행되어야 하는 부작용이라면 `transaction.on_commit()`으로 미룹니다.

```python
@transaction.atomic
def approve_order(order_id: int, gateway: ApprovalGateway) -> None:
    order = Order.objects.select_for_update().get(id=order_id)

    order.approve(approved_at=timezone.now())
    order.save(update_fields=["status", "approved_at"])

    transaction.on_commit(lambda: gateway.approve(order.external_id))
```

선택 기준은 명확해야 합니다.

| 상황 | 권장 방식 |
|---|---|
| 외부 API 성공이 상태 전이의 선조건 | Service에서 API 호출 후 모델 상태 변경 |
| DB 커밋 이후 알림/전송/동기화만 필요 | `transaction.on_commit()` |
| 재시도, 장애 복구, 중복 방지가 중요 | Outbox 패턴 |

작게 나누는 리팩터링 순서는 이렇게 잡는 게 안전합니다.

1. 모델 메서드 안의 외부 API 호출을 `ApprovalGateway` 같은 인터페이스 뒤로 추출합니다.
2. 모델 메서드에서 `save()`를 제거하고 상태 변경만 남깁니다.
3. 기존 호출부에 Application Service 함수를 만들고 `transaction.atomic()`을 둡니다.
4. `ValueError` 대신 `OrderCannotBeApproved` 같은 도메인 예외를 정의합니다.
5. 상태 문자열은 `TextChoices`로 고정하고, 가능한 규칙은 `clean()` 또는 `CheckConstraint`로 이중 방어합니다.
6. 외부 API 응답 필드명이 도메인에 침투했다면 Translator/ACL에서 도메인 용어로 변환합니다.
7. 테스트를 분리합니다: 모델 테스트는 DB/API 없이 상태 전이만, 서비스 테스트는 gateway mock으로 호출 순서와 저장 필드를 검증합니다.

검증은 최소한 이 정도가 필요합니다.

```bash
pytest tests/orders/test_order_model.py
pytest tests/orders/test_approve_order_service.py
python manage.py test
```

테스트 관점에서는 “모델 단위 테스트에서 외부 API mock이 필요하다”면 아직 분리가 덜 된 상태로 보면 됩니다.

---
> **관련 스킬 참조:**
> - Django 서비스 레이어와 transaction.on_commit → **implementation-django** 스킬
> - 부작용 없는 함수와 CQS 분리 → **implementation-cleancode** 스킬
> - 도메인 규칙/상태 전이 모델링 → **architecture-ddd** 스킬
> - 외부 API 격리/ACL/포트 어댑터 → **architecture-implementation-patterns** 스킬