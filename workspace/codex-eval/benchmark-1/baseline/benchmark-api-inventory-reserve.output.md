저장소가 비어 있고 `/private/tmp/dddjango-codex-eval/config.toml`도 없어 실제 파일 수정은 못 했습니다. 대신 Django Ninja 기준으로 바로 구현 가능한 API 설계를 정리합니다.

**핵심 설계**

재고 예약은 반드시 DB 트랜잭션 안에서 처리합니다.

- `Idempotency-Key` 헤더 필수
- 같은 사용자/클라이언트가 같은 key로 재요청하면 기존 결과 반환
- 같은 key인데 요청 body가 다르면 `409 Conflict`
- 재고 차감/예약 생성은 `select_for_update()`로 SKU row 잠금
- 예약 중복은 DB unique constraint로 최종 방어
- 재고 부족은 `409` 또는 `422`

**모델 예시**

```python
# inventory/models.py
from django.db import models


class StockItem(models.Model):
    sku = models.CharField(max_length=64, unique=True)
    available_qty = models.PositiveIntegerField(default=0)
    reserved_qty = models.PositiveIntegerField(default=0)
    version = models.PositiveIntegerField(default=0)


class Reservation(models.Model):
    class Status(models.TextChoices):
        RESERVED = "reserved"
        CANCELLED = "cancelled"
        EXPIRED = "expired"

    reservation_id = models.CharField(max_length=64, unique=True)
    sku = models.CharField(max_length=64)
    quantity = models.PositiveIntegerField()
    customer_id = models.CharField(max_length=64)
    status = models.CharField(max_length=20, choices=Status.choices)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["sku", "customer_id"],
                condition=models.Q(status="reserved"),
                name="uniq_active_reservation_per_customer_sku",
            )
        ]


class IdempotencyRecord(models.Model):
    key = models.CharField(max_length=128)
    scope = models.CharField(max_length=128)  # e.g. customer_id or API client id
    request_hash = models.CharField(max_length=64)
    status_code = models.PositiveSmallIntegerField(null=True, blank=True)
    response_body = models.JSONField(null=True, blank=True)
    locked_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["scope", "key"], name="uniq_idempotency_scope_key")
        ]
```

**Django Ninja API 예시**

```python
# inventory/api.py
import hashlib
import json
import uuid
from datetime import timedelta

from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Router, Schema

from .models import IdempotencyRecord, Reservation, StockItem

router = Router()


class ReserveRequest(Schema):
    sku: str
    quantity: int
    customer_id: str


class ReserveResponse(Schema):
    reservation_id: str
    sku: str
    quantity: int
    status: str
    expires_at: str


def hash_payload(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


@router.post("/reservations", response={201: ReserveResponse, 200: ReserveResponse, 409: dict})
def create_reservation(request, payload: ReserveRequest):
    idempotency_key = request.headers.get("Idempotency-Key")
    if not idempotency_key:
        return 409, {"detail": "Idempotency-Key header is required"}

    scope = payload.customer_id
    request_hash = hash_payload(payload.dict())

    with transaction.atomic():
        try:
            idem, created = IdempotencyRecord.objects.select_for_update().get_or_create(
                scope=scope,
                key=idempotency_key,
                defaults={
                    "request_hash": request_hash,
                    "locked_until": timezone.now() + timedelta(seconds=30),
                },
            )
        except IntegrityError:
            idem = IdempotencyRecord.objects.select_for_update().get(
                scope=scope,
                key=idempotency_key,
            )
            created = False

        if not created:
            if idem.request_hash != request_hash:
                return 409, {"detail": "Idempotency-Key was already used with different payload"}
            if idem.response_body is not None:
                return idem.status_code or 200, idem.response_body
            return 409, {"detail": "Request with this Idempotency-Key is already in progress"}

        stock = get_object_or_404(
            StockItem.objects.select_for_update(),
            sku=payload.sku,
        )

        if payload.quantity <= 0:
            response = {"detail": "quantity must be positive"}
            idem.status_code = 409
            idem.response_body = response
            idem.save(update_fields=["status_code", "response_body"])
            return 409, response

        if stock.available_qty < payload.quantity:
            response = {"detail": "insufficient stock"}
            idem.status_code = 409
            idem.response_body = response
            idem.save(update_fields=["status_code", "response_body"])
            return 409, response

        stock.available_qty -= payload.quantity
        stock.reserved_qty += payload.quantity
        stock.version += 1
        stock.save(update_fields=["available_qty", "reserved_qty", "version"])

        reservation = Reservation.objects.create(
            reservation_id=str(uuid.uuid4()),
            sku=payload.sku,
            quantity=payload.quantity,
            customer_id=payload.customer_id,
            status=Reservation.Status.RESERVED,
            expires_at=timezone.now() + timedelta(minutes=15),
        )

        response = {
            "reservation_id": reservation.reservation_id,
            "sku": reservation.sku,
            "quantity": reservation.quantity,
            "status": reservation.status,
            "expires_at": reservation.expires_at.isoformat(),
        }

        idem.status_code = 201
        idem.response_body = response
        idem.save(update_fields=["status_code", "response_body"])

        return 201, response
```

**동시성 처리 포인트**

`StockItem.objects.select_for_update()`가 핵심입니다. 같은 SKU에 대한 예약 요청이 동시에 들어와도 하나의 트랜잭션만 먼저 재고를 읽고 수정합니다. 나머지는 잠금 해제 후 최신 재고를 보고 처리하므로 oversell을 막습니다.

운영에서는 추가로 권장합니다.

- `IdempotencyRecord`에 TTL 정리 배치 추가
- 예약 만료 배치에서 `reserved_qty`를 `available_qty`로 복구
- `Idempotency-Key`는 최소 128비트 랜덤 문자열 요구
- PostgreSQL 사용 권장
- API 클라이언트 단위 `scope`를 `customer_id` 대신 인증된 `client_id/user_id`로 설정 권장