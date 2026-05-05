Fixture 경로 `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고, 현재 작업 디렉터리도 비어 있었습니다. 그래서 실제 파일 수정 대신 붙여 넣을 수 있는 설계 diff로 제안합니다. Django Ninja만 사용하고, endpoint는 얇게 두며 재고 예약 트랜잭션은 application service가 담당합니다.

```diff
diff --git a/apps/inventory/models.py b/apps/inventory/models.py
new file mode 100644
--- /dev/null
+++ b/apps/inventory/models.py
@@
+from django.conf import settings
+from django.db import models
+
+
+class StockItem(models.Model):
+    sku = models.CharField(max_length=64, unique=True)
+    available_quantity = models.PositiveIntegerField()
+    version = models.PositiveIntegerField(default=0)
+
+
+class StockReservation(models.Model):
+    class Status(models.TextChoices):
+        RESERVED = "reserved", "Reserved"
+        CANCELLED = "cancelled", "Cancelled"
+
+    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
+    stock_item = models.ForeignKey(StockItem, on_delete=models.PROTECT)
+    quantity = models.PositiveIntegerField()
+    status = models.CharField(max_length=16, choices=Status.choices)
+    created_at = models.DateTimeField(auto_now_add=True)
+
+
+class IdempotencyRecord(models.Model):
+    class State(models.TextChoices):
+        PROCESSING = "processing", "Processing"
+        COMPLETED = "completed", "Completed"
+        FAILED = "failed", "Failed"
+
+    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
+    key = models.CharField(max_length=128)
+    request_hash = models.CharField(max_length=64)
+    state = models.CharField(max_length=16, choices=State.choices)
+    status_code = models.PositiveSmallIntegerField(null=True, blank=True)
+    response_body = models.JSONField(null=True, blank=True)
+    created_at = models.DateTimeField(auto_now_add=True)
+    updated_at = models.DateTimeField(auto_now=True)
+
+    class Meta:
+        constraints = [
+            models.UniqueConstraint(
+                fields=["user", "key"],
+                name="uniq_idempotency_record_user_key",
+            ),
+        ]
+        indexes = [
+            models.Index(fields=["user", "key"]),
+            models.Index(fields=["state", "created_at"]),
+        ]
diff --git a/apps/inventory/schemas.py b/apps/inventory/schemas.py
new file mode 100644
--- /dev/null
+++ b/apps/inventory/schemas.py
@@
+from ninja import Schema
+
+
+class ReserveStockIn(Schema):
+    sku: str
+    quantity: int
+
+
+class ReservationOut(Schema):
+    id: int
+    sku: str
+    quantity: int
+    status: str
+
+
+class ProblemDetail(Schema):
+    type: str
+    title: str
+    status: int
+    detail: str
+    instance: str
diff --git a/apps/inventory/services.py b/apps/inventory/services.py
new file mode 100644
--- /dev/null
+++ b/apps/inventory/services.py
@@
+import hashlib
+import json
+from dataclasses import dataclass
+
+from django.contrib.auth.models import AbstractBaseUser
+from django.db import IntegrityError, transaction
+
+from .models import IdempotencyRecord, StockItem, StockReservation
+
+
+@dataclass(frozen=True)
+class ReservationResult:
+    status_code: int
+    body: dict
+
+
+class InventoryApplicationService:
+    def reserve(
+        self,
+        *,
+        user: AbstractBaseUser,
+        idempotency_key: str,
+        sku: str,
+        quantity: int,
+    ) -> ReservationResult:
+        payload = {"sku": sku, "quantity": quantity}
+        request_hash = hashlib.sha256(
+            json.dumps(payload, sort_keys=True).encode()
+        ).hexdigest()
+
+        with transaction.atomic():
+            try:
+                record = IdempotencyRecord.objects.create(
+                    user=user,
+                    key=idempotency_key,
+                    request_hash=request_hash,
+                    state=IdempotencyRecord.State.PROCESSING,
+                )
+            except IntegrityError:
+                record = IdempotencyRecord.objects.select_for_update().get(
+                    user=user,
+                    key=idempotency_key,
+                )
+            else:
+                record = IdempotencyRecord.objects.select_for_update().get(pk=record.pk)
+
+            if record.state == IdempotencyRecord.State.COMPLETED:
+                if record.request_hash != request_hash:
+                    return ReservationResult(409, {
+                        "type": "https://api.example.com/problems/idempotency-conflict",
+                        "title": "Idempotency key conflict",
+                        "status": 409,
+                        "detail": "Same Idempotency-Key was used with a different request body.",
+                    })
+                return ReservationResult(record.status_code, record.response_body)
+
+            item = StockItem.objects.select_for_update().get(sku=sku)
+            if quantity < 1 or item.available_quantity < quantity:
+                body = {
+                    "type": "https://api.example.com/problems/insufficient-stock",
+                    "title": "Insufficient stock",
+                    "status": 422,
+                    "detail": "Requested quantity cannot be reserved.",
+                }
+                record.state = IdempotencyRecord.State.COMPLETED
+                record.status_code = 422
+                record.response_body = body
+                record.save(update_fields=["state", "status_code", "response_body", "updated_at"])
+                return ReservationResult(422, body)
+
+            item.available_quantity -= quantity
+            item.version += 1
+            item.save(update_fields=["available_quantity", "version"])
+            reservation = StockReservation.objects.create(
+                user=user,
+                stock_item=item,
+                quantity=quantity,
+                status=StockReservation.Status.RESERVED,
+            )
+            body = {
+                "id": reservation.id,
+                "sku": item.sku,
+                "quantity": reservation.quantity,
+                "status": reservation.status,
+            }
+            record.state = IdempotencyRecord.State.COMPLETED
+            record.status_code = 201
+            record.response_body = body
+            record.save(update_fields=["state", "status_code", "response_body", "updated_at"])
+            return ReservationResult(201, body)
diff --git a/apps/inventory/api.py b/apps/inventory/api.py
new file mode 100644
--- /dev/null
+++ b/apps/inventory/api.py
@@
+from django.http import HttpRequest
+from ninja import Header, Router
+from ninja.security import django_auth
+
+from .schemas import ProblemDetail, ReservationOut, ReserveStockIn
+from .services import InventoryApplicationService
+
+router = Router(auth=django_auth, tags=["inventory"])
+
+
+@router.post(
+    "/reservations",
+    response={201: ReservationOut, 200: ReservationOut, 409: ProblemDetail, 422: ProblemDetail},
+)
+def reserve_stock(
+    request: HttpRequest,
+    payload: ReserveStockIn,
+    idempotency_key: str = Header(..., alias="Idempotency-Key"),
+) -> tuple[int, dict]:
+    result = InventoryApplicationService().reserve(
+        user=request.user,
+        idempotency_key=idempotency_key,
+        sku=payload.sku,
+        quantity=payload.quantity,
+    )
+    body = result.body | {"instance": request.path} if result.status_code >= 400 else result.body
+    return result.status_code, body
diff --git a/config/api.py b/config/api.py
new file mode 100644
--- /dev/null
+++ b/config/api.py
@@
+from ninja import NinjaAPI
+
+from apps.inventory.api import router as inventory_router
+
+api = NinjaAPI()
+api.add_router("/inventory", inventory_router)
```

동시성 전략은 `select_for_update()` 기반입니다. 같은 `Idempotency-Key` 요청은 `IdempotencyRecord(user, key)` unique constraint로 한 행에 수렴시키고, 그 행을 잠가 replay와 충돌 판정을 직렬화합니다. 재고 행도 `select_for_update()`로 잠가 차감 경쟁을 막습니다. 더 높은 처리량이 필요하면 `StockItem.version`을 이용한 optimistic locking으로 바꿀 수 있지만, 그 경우 `UPDATE ... WHERE version = old_version AND available_quantity >= quantity` 실패 시 재시도/409 정책을 명확히 둬야 합니다.

검증은 이 환경에서 실행하지 못했습니다. 적용 후 최소 실행 항목은 다음입니다.

```bash
python manage.py makemigrations inventory
python manage.py check
python manage.py test apps.inventory
```

테스트는 같은 key+같은 body 재요청이 동일 응답을 반환하는지, 같은 key+다른 body가 409인지, 동시 2요청에서 재고가 음수가 되지 않는지를 포함해야 합니다.

---
> **관련 스킬 참조:**
> - Django Ninja 구현/테스트 → **implementation-django-ninja** 스킬