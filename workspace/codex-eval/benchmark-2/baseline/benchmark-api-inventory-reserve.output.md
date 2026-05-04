작업 디렉터리 `/private/tmp/dddjango-codex-eval`에는 프로젝트 파일과 `config.toml`이 없습니다. 그래서 기존 코드에 패치하지는 못했고, Django Ninja 기준으로 바로 적용 가능한 설계안을 제안합니다.

**핵심 설계**

재고 예약 API는 다음 세 가지를 분리해서 처리하는 게 안전합니다.

1. `Inventory`
   실제 가용 재고 수량 관리

2. `InventoryReservation`
   예약 요청의 비즈니스 결과 저장

3. `IdempotencyRecord`
   중복 요청 방지 및 동일 응답 재사용

동시성 처리는 DB 트랜잭션 안에서 `select_for_update()`로 상품 재고 row를 잠그는 방식이 가장 단순하고 견고합니다.

```python
# models.py
from django.db import models
from django.utils import timezone


class Inventory(models.Model):
    sku = models.CharField(max_length=64, unique=True)
    available_quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)


class InventoryReservation(models.Model):
    class Status(models.TextChoices):
        RESERVED = "reserved"
        FAILED = "failed"
        CANCELLED = "cancelled"

    reservation_id = models.CharField(max_length=64, unique=True)
    sku = models.CharField(max_length=64)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices)
    reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)


class IdempotencyRecord(models.Model):
    key = models.CharField(max_length=128, unique=True)
    request_hash = models.CharField(max_length=64)
    response_body = models.JSONField(null=True, blank=True)
    status_code = models.PositiveSmallIntegerField(null=True, blank=True)
    locked_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
```

**API 계약**

`POST /inventory/reservations`

Header:

```http
Idempotency-Key: 7b4e7d42-...
```

Request:

```json
{
  "sku": "SKU-001",
  "quantity": 3
}
```

성공 응답:

```json
{
  "reservation_id": "rsv_01HX...",
  "sku": "SKU-001",
  "quantity": 3,
  "status": "reserved"
}
```

재고 부족:

```json
{
  "reservation_id": null,
  "sku": "SKU-001",
  "quantity": 3,
  "status": "failed",
  "reason": "insufficient_inventory"
}
```

**Django Ninja 구현 예시**

```python
# api.py
import hashlib
import json
import uuid

from django.db import IntegrityError, transaction
from django.utils import timezone
from ninja import NinjaAPI, Schema
from ninja.errors import HttpError

from .models import Inventory, InventoryReservation, IdempotencyRecord

api = NinjaAPI()


class ReservationIn(Schema):
    sku: str
    quantity: int


class ReservationOut(Schema):
    reservation_id: str | None
    sku: str
    quantity: int
    status: str
    reason: str | None = None


def hash_payload(payload: dict) -> str:
    normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode()).hexdigest()


@api.post("/inventory/reservations", response={200: ReservationOut, 201: ReservationOut})
def reserve_inventory(request, payload: ReservationIn):
    idem_key = request.headers.get("Idempotency-Key")
    if not idem_key:
        raise HttpError(400, "Idempotency-Key header is required")

    if payload.quantity <= 0:
        raise HttpError(400, "quantity must be greater than zero")

    request_body = payload.dict()
    request_hash = hash_payload(request_body)

    with transaction.atomic():
        try:
            idem = IdempotencyRecord.objects.create(
                key=idem_key,
                request_hash=request_hash,
                locked_until=timezone.now(),
            )
            is_first_request = True
        except IntegrityError:
            idem = (
                IdempotencyRecord.objects
                .select_for_update()
                .get(key=idem_key)
            )
            is_first_request = False

        if not is_first_request:
            if idem.request_hash != request_hash:
                raise HttpError(409, "Idempotency-Key was reused with different payload")

            if idem.completed_at:
                return idem.status_code or 200, idem.response_body

            raise HttpError(409, "Request with this Idempotency-Key is already processing")

        inventory = (
            Inventory.objects
            .select_for_update()
            .get(sku=payload.sku)
        )

        if inventory.available_quantity < payload.quantity:
            response = {
                "reservation_id": None,
                "sku": payload.sku,
                "quantity": payload.quantity,
                "status": "failed",
                "reason": "insufficient_inventory",
            }

            InventoryReservation.objects.create(
                reservation_id=f"rsv_{uuid.uuid4().hex}",
                sku=payload.sku,
                quantity=payload.quantity,
                status=InventoryReservation.Status.FAILED,
                reason="insufficient_inventory",
            )

            idem.response_body = response
            idem.status_code = 200
            idem.completed_at = timezone.now()
            idem.save(update_fields=["response_body", "status_code", "completed_at"])

            return 200, response

        inventory.available_quantity -= payload.quantity
        inventory.reserved_quantity += payload.quantity
        inventory.save(update_fields=["available_quantity", "reserved_quantity", "updated_at"])

        reservation = InventoryReservation.objects.create(
            reservation_id=f"rsv_{uuid.uuid4().hex}",
            sku=payload.sku,
            quantity=payload.quantity,
            status=InventoryReservation.Status.RESERVED,
        )

        response = {
            "reservation_id": reservation.reservation_id,
            "sku": payload.sku,
            "quantity": payload.quantity,
            "status": "reserved",
            "reason": None,
        }

        idem.response_body = response
        idem.status_code = 201
        idem.completed_at = timezone.now()
        idem.save(update_fields=["response_body", "status_code", "completed_at"])

        return 201, response
```

**중요 포인트**

- 같은 `Idempotency-Key` + 같은 payload: 이전 응답 그대로 반환
- 같은 `Idempotency-Key` + 다른 payload: `409 Conflict`
- 처리 중인 동일 key 재요청: `409 Conflict` 또는 `202 Accepted` 중 정책 선택 가능
- 재고 차감은 반드시 `transaction.atomic()` + `select_for_update()` 안에서 수행
- `IdempotencyRecord.key`는 DB unique constraint로 중복 생성 방지
- 실제 운영에서는 `IdempotencyRecord`에 TTL을 두고 오래된 key를 정리하는 배치 작업을 두는 게 좋습니다.