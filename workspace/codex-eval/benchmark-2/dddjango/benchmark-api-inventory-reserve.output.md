**설계 요약**

`POST /api/v1/inventory/reservations`는 재고를 “예약”하는 생성 API이므로 `Idempotency-Key` 헤더를 필수로 둡니다. 같은 사용자, 같은 endpoint, 같은 key는 DB `UniqueConstraint`로 1번만 처리하고, 재시도는 저장된 응답을 그대로 반환합니다. Ninja endpoint는 인증, Schema 검증, HTTP 변환만 담당하고, 재고 차감과 예약 생성은 application service가 트랜잭션 안에서 처리합니다.

```python
# inventory/models.py
class InventoryItem(models.Model):
    sku = models.CharField(max_length=64, unique=True)
    available_quantity = models.PositiveIntegerField()
    reserved_quantity = models.PositiveIntegerField(default=0)
    version = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(available_quantity__gte=0),
                name="inventory_available_quantity_gte_0",
            ),
        ]


class InventoryReservation(models.Model):
    class Status(models.TextChoices):
        RESERVED = "reserved", "Reserved"
        CANCELLED = "cancelled", "Cancelled"
        EXPIRED = "expired", "Expired"

    reservation_id = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    item = models.ForeignKey(InventoryItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=16, choices=Status, db_index=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)


class IdempotencyRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    endpoint = models.CharField(max_length=128)
    key = models.CharField(max_length=128)
    request_hash = models.CharField(max_length=64)
    response_status = models.PositiveSmallIntegerField(null=True, blank=True)
    response_body = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "endpoint", "key"],
                name="unique_idempotency_key_per_user_endpoint",
            ),
        ]
```

```python
# inventory/schemas.py
class ReserveInventoryIn(Schema):
    sku: str
    quantity: int = Field(gt=0)
    expires_at: datetime


class ReserveInventoryOut(Schema):
    reservation_id: UUID
    sku: str
    quantity: int
    status: str
    expires_at: datetime
```

```python
# inventory/services.py
class DuplicateIdempotencyConflict(Exception): ...
class InsufficientInventory(Exception): ...


class InventoryReservationService:
    endpoint = "POST /api/v1/inventory/reservations"

    @transaction.atomic
    def reserve(
        self,
        *,
        user,
        key: str,
        payload: ReserveInventoryIn,
    ) -> tuple[int, dict]:
        request_hash = hashlib.sha256(
            payload.json().encode()
        ).hexdigest()

        record, created = IdempotencyRecord.objects.get_or_create(
            user=user,
            endpoint=self.endpoint,
            key=key,
            defaults={"request_hash": request_hash},
        )

        record = (
            IdempotencyRecord.objects
            .select_for_update()
            .get(pk=record.pk)
        )

        if not created:
            if record.request_hash != request_hash:
                raise DuplicateIdempotencyConflict()
            if record.response_body is not None:
                return record.response_status, record.response_body

        item = (
            InventoryItem.objects
            .select_for_update()
            .get(sku=payload.sku)
        )

        if item.available_quantity < payload.quantity:
            raise InsufficientInventory()

        item.available_quantity -= payload.quantity
        item.reserved_quantity += payload.quantity
        item.version += 1
        item.save(update_fields=[
            "available_quantity",
            "reserved_quantity",
            "version",
        ])

        reservation = InventoryReservation.objects.create(
            user=user,
            item=item,
            quantity=payload.quantity,
            status=InventoryReservation.Status.RESERVED,
            expires_at=payload.expires_at,
        )

        body = {
            "reservation_id": reservation.reservation_id,
            "sku": item.sku,
            "quantity": reservation.quantity,
            "status": reservation.status,
            "expires_at": reservation.expires_at,
        }
        record.response_status = 201
        record.response_body = body
        record.save(update_fields=["response_status", "response_body"])

        return 201, body
```

```python
# inventory/api.py
router = Router(tags=["inventory"])


@router.post(
    "/reservations",
    response={201: ReserveInventoryOut, 200: ReserveInventoryOut},
    auth=django_auth,
)
def reserve_inventory(
    request,
    payload: ReserveInventoryIn,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
):
    try:
        status, body = InventoryReservationService().reserve(
            user=request.user,
            key=idempotency_key,
            payload=payload,
        )
        return status, body
    except DuplicateIdempotencyConflict:
        raise HttpError(409, "Idempotency-Key was reused with a different body")
    except InsufficientInventory:
        raise HttpError(409, "Insufficient inventory")
```

**동시성 전략**

기본안은 `select_for_update()`입니다. 같은 SKU 예약 요청은 `InventoryItem` row lock을 잡고 순차 처리되므로 oversell을 막습니다. 같은 idempotency key도 `IdempotencyRecord` row lock으로 중복 실행을 막습니다.

트래픽이 높고 충돌 재시도 처리가 가능하면 optimistic locking도 가능합니다. `version`을 조건에 넣어 `UPDATE inventory SET ... WHERE sku = ? AND version = ? AND available_quantity >= ?` 형태로 갱신하고, 영향 행이 0이면 `409` 또는 짧은 재시도를 반환합니다. 단순성과 정확성이 우선이면 `select_for_update()`가 더 낫습니다.

**검증 단계**

1. 같은 `Idempotency-Key`와 같은 body를 2번 보내면 두 번째 응답은 저장된 body를 반환한다.
2. 같은 key로 다른 body를 보내면 `409`가 난다.
3. 동시에 남은 수량보다 많이 예약해도 `available_quantity`가 음수가 되지 않는다.
4. DB에서 `unique_idempotency_key_per_user_endpoint` 제약이 실제 생성됐는지 migration SQL로 확인한다.

---
> **관련 스킬 참조:**
> - API 오류 형식/RFC 9457 정리 → **architecture-api** 스킬
> - 실제 Django Ninja 구현/테스트 작성 → **implementation-django-ninja** 스킬