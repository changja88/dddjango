implementation-django-ninja / architecture-api / architecture-db 스킬 기준으로 설계했습니다. 현재 `/private/tmp/dddjango-codex-eval`은 비어 있고 세션이 읽기 전용이라 파일 생성은 못 했습니다. 아래는 그대로 붙여 넣을 수 있는 Django Ninja 설계안입니다.

**주요 내용**

핵심 계약:

```http
POST /api/v1/inventory-reservations
Idempotency-Key: 01J...client-generated-key
Content-Type: application/json
```

```json
{
  "sku": "SKU-001",
  "quantity": 3,
  "expires_at": "2026-05-05T15:00:00+09:00"
}
```

응답:

- `201 Created`: 새 예약 생성
- `200 OK`: 같은 `Idempotency-Key` 재요청, 기존 응답 재생
- `409 Conflict`: 같은 key로 다른 payload 요청
- `422 Unprocessable Entity`: 재고 부족, 만료 시간이 부적절함
- `423 Locked` 또는 `409 Conflict`: 같은 key 처리 중 재요청 정책 선택 시

동시성 전략:

- 재고 행은 `select_for_update()`로 잠근다.
- 예약 생성과 재고 차감은 같은 `transaction.atomic()` 안에서 처리한다.
- 중복 요청은 `IdempotencyRecord(scope, key)` 유니크 제약으로 막는다.
- 같은 key 재요청은 저장된 `response_status`, `response_body`를 반환한다.
- payload hash가 다르면 같은 key 재사용 오류로 `409`를 반환한다.

`inventory/models.py`

```python
import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class InventoryItem(models.Model):
    sku = models.CharField(max_length=64, unique=True)
    available_quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sku"]
        indexes = [
            models.Index(fields=["sku"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(available_quantity__gte=0),
                name="inventory_available_quantity_gte_0",
            ),
            models.CheckConstraint(
                condition=Q(reserved_quantity__gte=0),
                name="inventory_reserved_quantity_gte_0",
            ),
        ]

    def __str__(self) -> str:
        return self.sku


class InventoryReservation(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"
        COMMITTED = "committed", "Committed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.PROTECT,
        related_name="reservations",
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    expires_at = models.DateTimeField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="inventory_reservations",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["item", "status", "expires_at"]),
            models.Index(fields=["created_by", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.item.sku}:{self.quantity}:{self.status}"


class IdempotencyRecord(models.Model):
    class Status(models.TextChoices):
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    scope = models.CharField(max_length=128)
    key = models.CharField(max_length=255)
    request_hash = models.CharField(max_length=64)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PROCESSING,
    )
    response_status = models.PositiveSmallIntegerField(null=True, blank=True)
    response_body = models.JSONField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="idempotency_records",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["scope", "key"],
                name="uniq_idempotency_scope_key",
            ),
        ]
        indexes = [
            models.Index(fields=["created_by", "scope", "key"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.scope}:{self.key}"
```

`inventory/schemas.py`

```python
from datetime import datetime
from uuid import UUID

from ninja import Schema


class ProblemDetail(Schema):
    type: str
    title: str
    status: int
    detail: str
    instance: str | None = None


class InventoryReservationCreateIn(Schema):
    sku: str
    quantity: int
    expires_at: datetime


class InventoryReservationOut(Schema):
    id: UUID
    sku: str
    quantity: int
    status: str
    expires_at: datetime
    created_at: datetime
```

`inventory/services.py`

```python
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import timedelta
from typing import Any

from django.db import transaction
from django.utils import timezone

from inventory.models import IdempotencyRecord, InventoryItem, InventoryReservation


@dataclass(frozen=True)
class ReservationResult:
    status_code: int
    body: dict[str, Any]


class IdempotencyConflict(Exception):
    pass


class InsufficientInventory(Exception):
    pass


def stable_payload_hash(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def create_inventory_reservation(
    *,
    user,
    idempotency_key: str,
    sku: str,
    quantity: int,
    expires_at,
) -> ReservationResult:
    scope = "inventory-reservations:create"
    request_hash = stable_payload_hash(
        {"sku": sku, "quantity": quantity, "expires_at": expires_at}
    )

    if quantity < 1:
        raise ValueError("quantity must be greater than 0")

    if expires_at <= timezone.now() + timedelta(minutes=1):
        raise ValueError("expires_at must be in the future")

    with transaction.atomic():
        idem, created = IdempotencyRecord.objects.select_for_update().get_or_create(
            scope=scope,
            key=idempotency_key,
            defaults={
                "request_hash": request_hash,
                "created_by": user,
            },
        )

        if not created:
            if idem.request_hash != request_hash:
                raise IdempotencyConflict("Idempotency-Key was reused with a different request")

            if idem.status == IdempotencyRecord.Status.COMPLETED:
                return ReservationResult(
                    status_code=idem.response_status,
                    body=idem.response_body,
                )

        item = InventoryItem.objects.select_for_update().get(sku=sku)

        if item.available_quantity < quantity:
            body = {
                "type": "https://api.example.com/problems/insufficient-inventory",
                "title": "Insufficient inventory",
                "status": 422,
                "detail": "Requested quantity exceeds available inventory.",
                "available_quantity": item.available_quantity,
            }
            idem.status = IdempotencyRecord.Status.COMPLETED
            idem.response_status = 422
            idem.response_body = body
            idem.save(update_fields=["status", "response_status", "response_body", "updated_at"])
            return ReservationResult(status_code=422, body=body)

        reservation = InventoryReservation.objects.create(
            item=item,
            quantity=quantity,
            expires_at=expires_at,
            created_by=user,
        )

        item.available_quantity -= quantity
        item.reserved_quantity += quantity
        item.save(update_fields=["available_quantity", "reserved_quantity"])

        body = {
            "id": str(reservation.id),
            "sku": item.sku,
            "quantity": reservation.quantity,
            "status": reservation.status,
            "expires_at": reservation.expires_at.isoformat(),
            "created_at": reservation.created_at.isoformat(),
        }

        idem.status = IdempotencyRecord.Status.COMPLETED
        idem.response_status = 201
        idem.response_body = body
        idem.save(update_fields=["status", "response_status", "response_body", "updated_at"])

        return ReservationResult(status_code=201, body=body)
```

`inventory/api.py`

```python
from typing import Any

from django.shortcuts import get_object_or_404
from ninja import Header, Router
from ninja.security import django_auth

from inventory.models import InventoryReservation
from inventory.schemas import (
    InventoryReservationCreateIn,
    InventoryReservationOut,
    ProblemDetail,
)
from inventory.services import (
    IdempotencyConflict,
    create_inventory_reservation,
)

router = Router(auth=django_auth)


@router.post(
    "/inventory-reservations",
    response={201: InventoryReservationOut, 200: InventoryReservationOut, 409: ProblemDetail, 422: ProblemDetail},
)
def create_reservation(
    request,
    payload: InventoryReservationCreateIn,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
) -> tuple[int, dict[str, Any]]:
    try:
        result = create_inventory_reservation(
            user=request.user,
            idempotency_key=idempotency_key,
            sku=payload.sku,
            quantity=payload.quantity,
            expires_at=payload.expires_at,
        )
        return result.status_code, result.body
    except IdempotencyConflict as exc:
        return 409, {
            "type": "https://api.example.com/problems/idempotency-key-conflict",
            "title": "Idempotency key conflict",
            "status": 409,
            "detail": str(exc),
        }
    except ValueError as exc:
        return 422, {
            "type": "https://api.example.com/problems/invalid-reservation-request",
            "title": "Invalid reservation request",
            "status": 422,
            "detail": str(exc),
        }


@router.get(
    "/inventory-reservations/{reservation_id}",
    response={200: InventoryReservationOut, 404: ProblemDetail},
)
def get_reservation(request, reservation_id: str) -> InventoryReservation:
    return get_object_or_404(
        InventoryReservation.objects.select_related("item"),
        id=reservation_id,
        created_by=request.user,
    )
```

`config/api.py`

```python
from ninja import NinjaAPI

from inventory.api import router as inventory_router

api = NinjaAPI(title="Inventory API", version="1.0.0")
api.add_router("/v1", inventory_router)
```

`config/urls.py`

```python
from django.urls import path

from config.api import api

urlpatterns = [
    path("api/", api.urls),
]
```

운영 정책은 PostgreSQL 기준을 권장합니다. `select_for_update()`는 SQLite에서 기대한 행 잠금 의미가 약하고, 재고 같은 동시성 민감 도메인은 PostgreSQL의 row-level lock과 유니크 제약을 전제로 잡는 편이 맞습니다.

검증은 이 정도가 최소입니다:

```bash
python manage.py makemigrations inventory
python manage.py migrate
python manage.py test inventory
```

테스트 케이스는 같은 `Idempotency-Key` 두 번 호출 시 같은 예약 ID 반환, 같은 key 다른 payload는 `409`, 동시 요청 N개 중 재고 수량만큼만 성공, 재고 부족 시 `422`를 확인하면 됩니다.

---
> **관련 스킬 참조:**
> - API 구현 세부화 → **implementation-django-ninja** 스킬
> - 트랜잭션/인덱스 검토 → **architecture-db** 스킬