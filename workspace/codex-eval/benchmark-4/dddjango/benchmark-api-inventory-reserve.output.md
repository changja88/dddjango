**설계안**

`POST /v1/inventory-reservations`는 재고 예약 생성 리소스입니다. `Idempotency-Key` 헤더를 필수로 받고, 같은 사용자/엔드포인트/key 조합은 같은 응답을 재생합니다.

```http
POST /api/v1/inventory-reservations
Idempotency-Key: 01HX...
Content-Type: application/json
```

```json
{ "sku": "SKU-001", "quantity": 2, "order_id": "ord_123" }
```

핵심 원칙은 3개입니다.

1. Ninja endpoint는 HTTP 입출력만 담당합니다.
2. application service가 유스케이스, 트랜잭션, 멱등성, 도메인 호출을 조율합니다.
3. 재고 동시성은 `select_for_update()`로 재고 row를 잠그거나, 고경합이면 optimistic locking으로 전환합니다.

**모델**

```python
class Inventory(models.Model):
    sku = models.CharField(max_length=64, unique=True)
    on_hand_qty = models.PositiveIntegerField()
    reserved_qty = models.PositiveIntegerField(default=0)
    version = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(on_hand_qty__gte=models.F("reserved_qty")),
                name="inventory_on_hand_gte_reserved",
            )
        ]


class InventoryReservation(models.Model):
    class Status(models.TextChoices):
        RESERVED = "reserved"
        REJECTED = "rejected"
        CANCELLED = "cancelled"

    reservation_id = models.UUIDField(default=uuid.uuid4, unique=True)
    sku = models.CharField(max_length=64)
    quantity = models.PositiveIntegerField()
    order_id = models.CharField(max_length=128)
    status = models.CharField(max_length=16, choices=Status, default=Status.RESERVED)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)


class IdempotencyRequest(models.Model):
    class Status(models.TextChoices):
        PROCESSING = "processing"
        SUCCEEDED = "succeeded"
        FAILED = "failed"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    key = models.CharField(max_length=255)
    route = models.CharField(max_length=128)
    request_hash = models.CharField(max_length=64)
    status = models.CharField(max_length=16, choices=Status)
    response_status = models.PositiveSmallIntegerField(null=True)
    response_body = models.JSONField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "route", "key"],
                name="uniq_idempotency_user_route_key",
            )
        ]
        indexes = [
            models.Index(fields=["user", "route", "key"]),
        ]
```

**Application Service**

```python
@dataclass(frozen=True)
class ReserveInventoryCommand:
    user_id: int
    sku: str
    quantity: int
    order_id: str
    idempotency_key: str
    request_hash: str


class InventoryApplicationService:
    route = "POST /v1/inventory-reservations"

    @transaction.atomic
    def reserve(self, cmd: ReserveInventoryCommand) -> tuple[int, dict]:
        idem = self._lock_or_create_idempotency(cmd)

        if idem.request_hash != cmd.request_hash:
            return 409, {"type": "about:blank", "title": "Idempotency conflict", "status": 409}

        if idem.status in {
            IdempotencyRequest.Status.SUCCEEDED,
            IdempotencyRequest.Status.FAILED,
        }:
            return idem.response_status, idem.response_body

        inventory = (
            Inventory.objects
            .select_for_update()
            .get(sku=cmd.sku)
        )

        available = inventory.on_hand_qty - inventory.reserved_qty
        if available < cmd.quantity:
            body = {"type": "about:blank", "title": "Insufficient inventory", "status": 409}
            self._finish(idem, IdempotencyRequest.Status.FAILED, 409, body)
            return 409, body

        inventory.reserved_qty = F("reserved_qty") + cmd.quantity
        inventory.save(update_fields=["reserved_qty"])

        reservation = InventoryReservation.objects.create(
            sku=cmd.sku,
            quantity=cmd.quantity,
            order_id=cmd.order_id,
            created_by_id=cmd.user_id,
        )
        body = {"reservation_id": str(reservation.reservation_id), "status": "reserved"}
        self._finish(idem, IdempotencyRequest.Status.SUCCEEDED, 201, body)
        return 201, body

    def _lock_or_create_idempotency(self, cmd):
        try:
            return IdempotencyRequest.objects.create(
                user_id=cmd.user_id,
                route=self.route,
                key=cmd.idempotency_key,
                request_hash=cmd.request_hash,
                status=IdempotencyRequest.Status.PROCESSING,
            )
        except IntegrityError:
            return (
                IdempotencyRequest.objects
                .select_for_update()
                .get(user_id=cmd.user_id, route=self.route, key=cmd.idempotency_key)
            )

    def _finish(self, idem, status, response_status, response_body):
        idem.status = status
        idem.response_status = response_status
        idem.response_body = response_body
        idem.save(update_fields=["status", "response_status", "response_body"])
```

중요한 점: 실패 응답도 `IdempotencyRequest`에 저장한 뒤 예외를 다시 던지지 않습니다. 예외를 던지면 `atomic()` rollback으로 실패 응답 저장이 사라질 수 있습니다.

**Django Ninja**

```python
class ReserveInventoryIn(Schema):
    sku: str
    quantity: int
    order_id: str


class ReservationOut(Schema):
    reservation_id: str
    status: str


router = Router(tags=["inventory-reservations"])


@router.post(
    "/inventory-reservations",
    response={201: ReservationOut, 409: dict},
    auth=django_auth,
)
def reserve_inventory(
    request: HttpRequest,
    payload: ReserveInventoryIn,
    idempotency_key: Header[str],
):
    body = payload.dict()
    status, result = InventoryApplicationService().reserve(
        ReserveInventoryCommand(
            user_id=request.user.id,
            sku=payload.sku,
            quantity=payload.quantity,
            order_id=payload.order_id,
            idempotency_key=idempotency_key,
            request_hash=hashlib.sha256(
                json.dumps(body, sort_keys=True).encode()
            ).hexdigest(),
        )
    )
    return status, result
```

**동시성 선택**

`select_for_update()`는 예약 대상 `Inventory` row를 직렬화하므로 단순하고 정확합니다. PostgreSQL 기준 Read Committed에서도 동일 SKU 동시 예약 초과를 막습니다.

고경합 SKU에서 lock wait가 커지면 optimistic locking으로 바꿉니다.

```python
updated = Inventory.objects.filter(
    sku=cmd.sku,
    version=current_version,
    on_hand_qty__gte=F("reserved_qty") + cmd.quantity,
).update(
    reserved_qty=F("reserved_qty") + cmd.quantity,
    version=F("version") + 1,
)
```

`updated == 0`이면 재조회 후 재시도하거나 409를 반환합니다.

**검증 단계**

```bash
python manage.py makemigrations
python manage.py check
pytest
pytest tests/test_inventory_reservations_api.py
```

테스트는 최소한 같은 `Idempotency-Key` 재요청이 같은 `reservation_id`를 반환하는지, 다른 body로 같은 key를 쓰면 409인지, 동시 요청 합계가 `on_hand_qty`를 넘지 않는지 검증해야 합니다.

---
> **관련 스킬 참조:**
> - API 구현 세부화 → **implementation-django-ninja** 스킬