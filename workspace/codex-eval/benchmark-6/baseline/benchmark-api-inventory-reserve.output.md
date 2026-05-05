**주요 내용**

지정된 fixture 경로 `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고, 작업 디렉터리 `/private/tmp/dddjango-codex-eval`도 비어 있었습니다. 그래서 기존 코드에 맞춘 수정은 할 수 없어, `apps/inventory` 앱을 추가한다는 가정으로 적용 가능한 unified diff를 제안합니다.

설계 요점:
- `POST /api/inventory/reservations/`
- 필수 헤더: `Idempotency-Key`
- 같은 key + 같은 body 재시도: 저장된 응답 재사용
- 같은 key + 다른 body: `409 Conflict`
- 재고 동시성: `transaction.atomic()` + `select_for_update()`
- 오류 응답: RFC 9457 Problem Details

```diff
diff --git a/apps/inventory/models.py b/apps/inventory/models.py
new file mode 100644
--- /dev/null
+++ b/apps/inventory/models.py
@@ -0,0 +1,92 @@
+import uuid
+
+from django.conf import settings
+from django.core.validators import MinValueValidator
+from django.db import models
+from django.utils import timezone
+
+
+class StockItem(models.Model):
+    sku = models.CharField(max_length=64, unique=True)
+    total_quantity = models.PositiveIntegerField()
+    reserved_quantity = models.PositiveIntegerField(default=0)
+    created_at = models.DateTimeField(auto_now_add=True)
+    updated_at = models.DateTimeField(auto_now=True)
+
+    class Meta:
+        ordering = ["sku"]
+        indexes = [models.Index(fields=["sku"])]
+        constraints = [
+            models.CheckConstraint(
+                check=models.Q(reserved_quantity__lte=models.F("total_quantity")),
+                name="stock_reserved_lte_total",
+            )
+        ]
+
+    def __str__(self) -> str:
+        return self.sku
+
+    @property
+    def available_quantity(self) -> int:
+        return self.total_quantity - self.reserved_quantity
+
+    def reserve(self, quantity: int) -> None:
+        if quantity <= 0:
+            raise ValueError("quantity must be greater than zero")
+        if self.available_quantity < quantity:
+            raise InsufficientStockError(self.sku, self.available_quantity, quantity)
+        self.reserved_quantity += quantity
+
+
+class Reservation(models.Model):
+    class Status(models.TextChoices):
+        ACTIVE = "active", "Active"
+        CANCELLED = "cancelled", "Cancelled"
+
+    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
+    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
+    stock_item = models.ForeignKey(StockItem, on_delete=models.PROTECT)
+    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
+    status = models.CharField(
+        max_length=16,
+        choices=Status.choices,
+        default=Status.ACTIVE,
+    )
+    created_at = models.DateTimeField(auto_now_add=True)
+
+    class Meta:
+        ordering = ["-created_at"]
+        indexes = [
+            models.Index(fields=["user", "-created_at"]),
+            models.Index(fields=["stock_item", "status"]),
+        ]
+
+    def __str__(self) -> str:
+        return f"{self.stock_item.sku}:{self.quantity}"
+
+
+class IdempotencyRecord(models.Model):
+    class Status(models.TextChoices):
+        PROCESSING = "processing", "Processing"
+        COMPLETED = "completed", "Completed"
+        FAILED = "failed", "Failed"
+
+    key = models.CharField(max_length=255)
+    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
+    request_hash = models.CharField(max_length=64)
+    status = models.CharField(max_length=16, choices=Status.choices)
+    response_status = models.PositiveSmallIntegerField(null=True, blank=True)
+    response_body = models.JSONField(null=True, blank=True)
+    expires_at = models.DateTimeField()
+    created_at = models.DateTimeField(auto_now_add=True)
+    updated_at = models.DateTimeField(auto_now=True)
+
+    class Meta:
+        ordering = ["-created_at"]
+        constraints = [
+            models.UniqueConstraint(
+                fields=["user", "key"],
+                name="unique_idempotency_key_per_user",
+            )
+        ]
+        indexes = [models.Index(fields=["expires_at"])]
+
+    def __str__(self) -> str:
+        return self.key
+
+    @classmethod
+    def default_expires_at(cls):
+        return timezone.now() + timezone.timedelta(hours=24)
+
+
+class InsufficientStockError(Exception):
+    def __init__(self, sku: str, available: int, requested: int) -> None:
+        self.sku = sku
+        self.available = available
+        self.requested = requested
diff --git a/apps/inventory/services.py b/apps/inventory/services.py
new file mode 100644
--- /dev/null
+++ b/apps/inventory/services.py
@@ -0,0 +1,91 @@
+import hashlib
+import json
+from dataclasses import dataclass
+
+from django.db import IntegrityError, transaction
+from django.utils import timezone
+
+from apps.inventory.models import (
+    IdempotencyRecord,
+    InsufficientStockError,
+    Reservation,
+    StockItem,
+)
+
+
+class IdempotencyConflictError(Exception):
+    pass
+
+
+class IdempotencyInProgressError(Exception):
+    pass
+
+
+@dataclass(frozen=True)
+class ReservationResult:
+    status_code: int
+    body: dict
+
+
+def reservation_request_hash(payload: dict) -> str:
+    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
+    return hashlib.sha256(encoded).hexdigest()
+
+
+def reserve_stock(*, user, sku: str, quantity: int, idempotency_key: str) -> ReservationResult:
+    payload_hash = reservation_request_hash({"sku": sku, "quantity": quantity})
+
+    with transaction.atomic():
+        record = _get_or_create_locked_record(user, idempotency_key, payload_hash)
+
+        if record.request_hash != payload_hash:
+            raise IdempotencyConflictError
+
+        if record.status in {
+            IdempotencyRecord.Status.COMPLETED,
+            IdempotencyRecord.Status.FAILED,
+        }:
+            return ReservationResult(record.response_status, record.response_body)
+
+        stock_item = StockItem.objects.select_for_update().get(sku=sku)
+        stock_item.reserve(quantity)
+        stock_item.save(update_fields=["reserved_quantity", "updated_at"])
+
+        reservation = Reservation.objects.create(
+            user=user,
+            stock_item=stock_item,
+            quantity=quantity,
+        )
+        body = {
+            "id": str(reservation.id),
+            "sku": stock_item.sku,
+            "quantity": reservation.quantity,
+            "status": reservation.status,
+            "created_at": reservation.created_at.isoformat().replace("+00:00", "Z"),
+        }
+        record.status = IdempotencyRecord.Status.COMPLETED
+        record.response_status = 201
+        record.response_body = body
+        record.save(
+            update_fields=[
+                "status",
+                "response_status",
+                "response_body",
+                "updated_at",
+            ]
+        )
+        return ReservationResult(201, body)
+
+
+def _get_or_create_locked_record(user, key: str, payload_hash: str) -> IdempotencyRecord:
+    try:
+        record, _ = IdempotencyRecord.objects.select_for_update().get_or_create(
+            user=user,
+            key=key,
+            defaults={
+                "request_hash": payload_hash,
+                "status": IdempotencyRecord.Status.PROCESSING,
+                "expires_at": IdempotencyRecord.default_expires_at(),
+            },
+        )
+    except IntegrityError:
+        record = IdempotencyRecord.objects.select_for_update().get(user=user, key=key)
+
+    if record.expires_at <= timezone.now():
+        raise IdempotencyConflictError
+    return record
diff --git a/apps/inventory/schemas.py b/apps/inventory/schemas.py
new file mode 100644
--- /dev/null
+++ b/apps/inventory/schemas.py
@@ -0,0 +1,27 @@
+from datetime import datetime
+from uuid import UUID
+
+from ninja import Schema
+from pydantic import Field
+
+
+class ReservationCreateIn(Schema):
+    sku: str = Field(min_length=1, max_length=64)
+    quantity: int = Field(gt=0)
+
+
+class ReservationOut(Schema):
+    id: UUID
+    sku: str
+    quantity: int
+    status: str
+    created_at: datetime
+
+
+class ProblemDetail(Schema):
+    type: str = "about:blank"
+    title: str
+    status: int
+    detail: str
+    instance: str
diff --git a/apps/inventory/api.py b/apps/inventory/api.py
new file mode 100644
--- /dev/null
+++ b/apps/inventory/api.py
@@ -0,0 +1,88 @@
+from django.http import HttpRequest, JsonResponse
+from django.shortcuts import get_object_or_404
+from ninja import Header, Router
+from ninja.security import django_auth
+
+from apps.inventory.models import InsufficientStockError, StockItem
+from apps.inventory.schemas import ProblemDetail, ReservationCreateIn, ReservationOut
+from apps.inventory.services import (
+    IdempotencyConflictError,
+    reserve_stock,
+)
+
+router = Router(tags=["inventory"], auth=django_auth)
+
+
+@router.post(
+    "/reservations/",
+    response={200: ReservationOut, 201: ReservationOut, 409: ProblemDetail, 422: ProblemDetail},
+)
+def create_reservation(
+    request: HttpRequest,
+    payload: ReservationCreateIn,
+    idempotency_key: str = Header(..., alias="Idempotency-Key"),
+):
+    try:
+        result = reserve_stock(
+            user=request.user,
+            sku=payload.sku,
+            quantity=payload.quantity,
+            idempotency_key=idempotency_key,
+        )
+    except StockItem.DoesNotExist:
+        return problem_response(
+            request,
+            status=422,
+            title="Unknown SKU",
+            detail="The requested SKU cannot be reserved.",
+            type_="https://api.example.com/problems/unknown-sku",
+        )
+    except InsufficientStockError as exc:
+        return problem_response(
+            request,
+            status=409,
+            title="Insufficient Stock",
+            detail=(
+                f"SKU {exc.sku} has {exc.available} available, "
+                f"but {exc.requested} was requested."
+            ),
+            type_="https://api.example.com/problems/insufficient-stock",
+        )
+    except IdempotencyConflictError:
+        return problem_response(
+            request,
+            status=409,
+            title="Idempotency Key Conflict",
+            detail="The Idempotency-Key was already used for a different request.",
+            type_="https://api.example.com/problems/idempotency-key-conflict",
+        )
+
+    return result.status_code, result.body
+
+
+@router.get("/stock/{sku}", response={200: dict, 404: ProblemDetail})
+def get_stock(request: HttpRequest, sku: str):
+    stock_item = get_object_or_404(StockItem, sku=sku)
+    return {
+        "sku": stock_item.sku,
+        "total_quantity": stock_item.total_quantity,
+        "reserved_quantity": stock_item.reserved_quantity,
+        "available_quantity": stock_item.available_quantity,
+    }
+
+
+def problem_response(
+    request: HttpRequest,
+    *,
+    status: int,
+    title: str,
+    detail: str,
+    type_: str,
+) -> JsonResponse:
+    return JsonResponse(
+        {
+            "type": type_,
+            "title": title,
+            "status": status,
+            "detail": detail,
+            "instance": request.path,
+        },
+        status=status,
+        content_type="application/problem+json",
+    )
diff --git a/config/api.py b/config/api.py
new file mode 100644
--- /dev/null
+++ b/config/api.py
@@ -0,0 +1,6 @@
+from ninja import NinjaAPI
+
+from apps.inventory.api import router as inventory_router
+
+api = NinjaAPI(title="Inventory API", version="1.0.0")
+api.add_router("/inventory/", inventory_router)
diff --git a/config/urls.py b/config/urls.py
new file mode 100644
--- /dev/null
+++ b/config/urls.py
@@ -0,0 +1,7 @@
+from django.urls import path
+
+from config.api import api
+
+urlpatterns = [
+    path("api/", api.urls),
+]
```

검증은 실행하지 못했습니다. fixture와 Django 프로젝트 파일이 없고, 현재 sandbox가 read-only입니다. 실제 프로젝트에 적용한 뒤 최소한 아래를 실행하세요.

```bash
python manage.py makemigrations inventory
python manage.py check
pytest
```

---
> **관련 스킬 참조:**
> - 동시성/인덱스/트랜잭션 검토 → **architecture-db** 스킬