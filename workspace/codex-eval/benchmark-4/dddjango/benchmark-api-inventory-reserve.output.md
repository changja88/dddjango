**재고 예약 API 설계**

`POST /v1/inventory-reservations`로 설계합니다. URL에는 `reserve` 같은 동사를 넣지 않고, 생성되는 리소스인 `inventory-reservations`를 사용합니다.

응답 기준:

- `201 Created`: 최초 예약 생성
- `200 OK`: 같은 `Idempotency-Key`와 같은 요청 본문 재전송, 저장된 응답 반환
- `409 Conflict`: 같은 key를 다른 payload로 재사용, 또는 아직 처리 중
- `422 Unprocessable Entity`: 재고 부족
- 오류 응답은 RFC 9457 Problem Details

핵심 모델:

```python
class IdempotencyKey(models.Model):
    class Status(models.TextChoices):
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"

    actor_id = models.CharField(max_length=64)
    scope = models.CharField(max_length=100)
    key = models.CharField(max_length=255)
    request_hash = models.CharField(max_length=64)
    status = models.CharField(max_length=20, choices=Status, default=Status.PROCESSING)
    response_status = models.PositiveSmallIntegerField(null=True, blank=True)
    response_body = models.JSONField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["actor_id", "scope", "key"],
                name="uniq_idempotency_actor_scope_key",
            ),
        ]


class Inventory(models.Model):
    sku_id = models.BigIntegerField(unique=True)
    available_quantity = models.PositiveIntegerField()
    reserved_quantity = models.PositiveIntegerField(default=0)
    version = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(available_quantity__gte=0),
                name="inventory_available_non_negative",
            ),
        ]


class InventoryReservation(models.Model):
    class Status(models.TextChoices):
        RESERVED = "reserved", "Reserved"
        CANCELLED = "cancelled", "Cancelled"

    sku_id = models.BigIntegerField()
    user_id = models.BigIntegerField()
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status)
    idempotency_key = models.OneToOneField(IdempotencyKey, on_delete=models.PROTECT)
```

Ninja endpoint는 얇게 유지하고, 멱등성/트랜잭션/동시성은 application service가 담당합니다.

```python
from ninja import Header, Router, Schema
from ninja.security import django_auth
from pydantic import Field

router = Router(tags=["inventory"], auth=django_auth)


class ReservationCreateIn(Schema):
    sku_id: int
    quantity: int = Field(gt=0)


class ReservationOut(Schema):
    id: int
    sku_id: int
    quantity: int
    status: str


@router.post(
    "/inventory-reservations",
    response={201: ReservationOut, 200: ReservationOut},
)
def create_inventory_reservation(
    request,
    payload: ReservationCreateIn,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
):
    result = reservation_create(
        actor_id=str(request.user.id),
        idempotency_key=idempotency_key,
        payload=payload,
    )
    return result.status_code, result.body
```

서비스 계층:

```python
@dataclass(frozen=True)
class ServiceResult:
    status_code: int
    body: dict


def reservation_create(*, actor_id: str, idempotency_key: str, payload) -> ServiceResult:
    scope = "POST:/v1/inventory-reservations"
    request_hash = hash_payload(payload)

    with transaction.atomic():
        try:
            idem = IdempotencyKey.objects.create(
                actor_id=actor_id,
                scope=scope,
                key=idempotency_key,
                request_hash=request_hash,
            )
            created = True
        except IntegrityError:
            created = False
            idem = IdempotencyKey.objects.select_for_update().get(
                actor_id=actor_id,
                scope=scope,
                key=idempotency_key,
            )

        if not created:
            if idem.request_hash != request_hash:
                raise IdempotencyConflictError()
            if idem.status == IdempotencyKey.Status.COMPLETED:
                return ServiceResult(idem.response_status, idem.response_body)
            raise RequestAlreadyProcessingError()

        inventory = (
            Inventory.objects.select_for_update()
            .get(sku_id=payload.sku_id)
        )

        if inventory.available_quantity < payload.quantity:
            body = problem_detail("Insufficient stock", 422)
            idem.status = IdempotencyKey.Status.COMPLETED
            idem.response_status = 422
            idem.response_body = body
            idem.save(update_fields=["status", "response_status", "response_body"])
            raise InsufficientStockError(body)

        inventory.available_quantity -= payload.quantity
        inventory.reserved_quantity += payload.quantity
        inventory.version += 1
        inventory.save(
            update_fields=["available_quantity", "reserved_quantity", "version"]
        )

        reservation = InventoryReservation.objects.create(
            sku_id=payload.sku_id,
            user_id=int(actor_id),
            quantity=payload.quantity,
            status=InventoryReservation.Status.RESERVED,
            idempotency_key=idem,
        )

        body = {
            "id": reservation.id,
            "sku_id": reservation.sku_id,
            "quantity": reservation.quantity,
            "status": reservation.status,
        }
        idem.status = IdempotencyKey.Status.COMPLETED
        idem.response_status = 201
        idem.response_body = body
        idem.save(update_fields=["status", "response_status", "response_body"])

    return ServiceResult(201, body)
```

동시성 전략은 기본적으로 `select_for_update()`를 권장합니다. 같은 SKU 예약 요청들이 같은 `Inventory` 행에서 직렬화되어 oversell을 막습니다. 트래픽이 높고 충돌이 잦지 않다면 optimistic locking도 가능합니다: `version` 조건과 `available_quantity__gte=quantity` 조건을 건 `update()`를 실행하고, 갱신 row 수가 `0`이면 재시도하거나 `409/422`로 처리합니다.

검증은 최소한 다음 테스트가 필요합니다.

```text
1. 같은 Idempotency-Key + 같은 payload 2회 요청 -> Reservation 1개, 두 번째는 200과 동일 body
2. 같은 Idempotency-Key + 다른 payload -> 409 Problem Details
3. 동시에 남은 재고보다 많은 예약 요청 -> available_quantity 음수 불가, 성공 수 제한
4. 재고 부족 -> 422, 재시도 시 같은 key면 같은 실패 응답
5. unique constraint 위반 경로에서도 중복 Reservation 생성 없음
```

---
> **관련 스킬 참조:**
> - Django Ninja Schema/Router 구현 → **implementation-django-ninja** 스킬
> - 트랜잭션과 unique constraint 설계 → **architecture-db** 스킬
> - 애그리거트/서비스 책임 분리 → **architecture-ddd** 스킬