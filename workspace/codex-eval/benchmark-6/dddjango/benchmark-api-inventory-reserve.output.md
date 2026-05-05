Fixture 확인 결과: `/Users/hyun/Desktop/dddjango/none` 경로는 존재하지 않았고, 현재 작업 디렉터리에도 읽을 프로젝트 파일이 없었습니다. 그래서 아래는 `inventory` 앱이 있다고 가정한 read-only unified diff입니다. 핵심은 `IdempotencyKey.key` unique constraint, `select_for_update()` 기반 재고 행 잠금, Ninja endpoint와 application service 분리입니다.

```diff
diff --git a/inventory/models.py b/inventory/models.py
new file mode 100644
--- /dev/null
+++ b/inventory/models.py
@@
+from django.db import models
+from django.utils import timezone
+
+
+class InventoryItem(models.Model):
+    sku = models.CharField(max_length=64, unique=True)
+    available_quantity = models.PositiveIntegerField()
+    version = models.PositiveIntegerField(default=0)
+
+    class Meta:
+        indexes = [models.Index(fields=["sku"])]
+        constraints = [
+            models.CheckConstraint(
+                condition=models.Q(available_quantity__gte=0),
+                name="inventory_available_quantity_gte_0",
+            )
+        ]
+
+
+class InventoryReservation(models.Model):
+    class Status(models.TextChoices):
+        RESERVED = "reserved", "Reserved"
+
+    sku = models.CharField(max_length=64)
+    quantity = models.PositiveIntegerField()
+    status = models.CharField(max_length=16, choices=Status.choices)
+    created_at = models.DateTimeField(auto_now_add=True)
+
+    class Meta:
+        indexes = [models.Index(fields=["sku", "created_at"])]
+        constraints = [
+            models.CheckConstraint(
+                condition=models.Q(quantity__gt=0),
+                name="reservation_quantity_gt_0",
+            )
+        ]
+
+
+class IdempotencyKey(models.Model):
+    class Status(models.TextChoices):
+        STARTED = "started", "Started"
+        COMPLETED = "completed", "Completed"
+
+    key = models.CharField(max_length=128, unique=True)
+    request_hash = models.CharField(max_length=64)
+    status = models.CharField(max_length=16, choices=Status.choices)
+    reservation = models.ForeignKey(
+        InventoryReservation,
+        null=True,
+        blank=True,
+        on_delete=models.PROTECT,
+    )
+    error_code = models.CharField(max_length=32, blank=True)
+    created_at = models.DateTimeField(auto_now_add=True)
+    completed_at = models.DateTimeField(null=True, blank=True)
+
+    class Meta:
+        constraints = [
+            models.UniqueConstraint(
+                fields=["key"],
+                name="uq_inventory_idempotency_key",
+            )
+        ]
diff --git a/inventory/application.py b/inventory/application.py
new file mode 100644
--- /dev/null
+++ b/inventory/application.py
@@
+import hashlib
+from dataclasses import dataclass
+
+from django.db import transaction
+from django.utils import timezone
+
+from .models import IdempotencyKey, InventoryItem, InventoryReservation
+
+
+@dataclass(frozen=True)
+class ReserveInventoryResult:
+    code: str
+    reservation_id: int | None = None
+    sku: str = ""
+    quantity: int = 0
+
+
+def reserve_inventory(
+    *,
+    sku: str,
+    quantity: int,
+    idempotency_key: str,
+) -> ReserveInventoryResult:
+    request_hash = hashlib.sha256(f"{sku}:{quantity}".encode()).hexdigest()
+
+    with transaction.atomic():
+        idem, created = IdempotencyKey.objects.select_for_update().get_or_create(
+            key=idempotency_key,
+            defaults={
+                "request_hash": request_hash,
+                "status": IdempotencyKey.Status.STARTED,
+            },
+        )
+
+        if not created:
+            if idem.request_hash != request_hash:
+                return ReserveInventoryResult(code="idempotency_conflict")
+            if idem.status == IdempotencyKey.Status.COMPLETED:
+                if idem.reservation_id:
+                    return ReserveInventoryResult(
+                        code="replayed",
+                        reservation_id=idem.reservation_id,
+                        sku=idem.reservation.sku,
+                        quantity=idem.reservation.quantity,
+                    )
+                return ReserveInventoryResult(code=idem.error_code)
+            return ReserveInventoryResult(code="request_in_progress")
+
+        item = InventoryItem.objects.select_for_update().filter(sku=sku).first()
+        if item is None:
+            idem.status = IdempotencyKey.Status.COMPLETED
+            idem.error_code = "sku_not_found"
+            idem.completed_at = timezone.now()
+            idem.save(update_fields=["status", "error_code", "completed_at"])
+            return ReserveInventoryResult(code="sku_not_found")
+
+        if item.available_quantity < quantity:
+            idem.status = IdempotencyKey.Status.COMPLETED
+            idem.error_code = "insufficient_stock"
+            idem.completed_at = timezone.now()
+            idem.save(update_fields=["status", "error_code", "completed_at"])
+            return ReserveInventoryResult(code="insufficient_stock")
+
+        item.available_quantity -= quantity
+        item.version += 1
+        item.save(update_fields=["available_quantity", "version"])
+
+        reservation = InventoryReservation.objects.create(
+            sku=sku,
+            quantity=quantity,
+            status=InventoryReservation.Status.RESERVED,
+        )
+        idem.status = IdempotencyKey.Status.COMPLETED
+        idem.reservation = reservation
+        idem.completed_at = timezone.now()
+        idem.save(update_fields=["status", "reservation", "completed_at"])
+
+        return ReserveInventoryResult(
+            code="reserved",
+            reservation_id=reservation.id,
+            sku=sku,
+            quantity=quantity,
+        )
diff --git a/inventory/api.py b/inventory/api.py
new file mode 100644
--- /dev/null
+++ b/inventory/api.py
@@
+from django.http import HttpRequest
+from ninja import Field, Header, Router, Schema
+from ninja.security import django_auth
+
+from .application import ReserveInventoryResult, reserve_inventory
+
+router = Router(tags=["inventory"], auth=django_auth)
+
+
+class ReserveInventoryIn(Schema):
+    sku: str = Field(..., min_length=1)
+    quantity: int = Field(..., ge=1)
+
+
+class ReservationOut(Schema):
+    id: int
+    sku: str
+    quantity: int
+
+
+class ProblemDetail(Schema):
+    type: str
+    title: str
+    status: int
+    detail: str
+    instance: str
+
+
+def problem(status: int, title: str, detail: str, instance: str) -> ProblemDetail:
+    return ProblemDetail(
+        type=f"https://api.example.com/problems/{title.lower().replace(' ', '-')}",
+        title=title,
+        status=status,
+        detail=detail,
+        instance=instance,
+    )
+
+
+@router.post(
+    "/reservations",
+    response={
+        200: ReservationOut,
+        201: ReservationOut,
+        404: ProblemDetail,
+        409: ProblemDetail,
+        422: ProblemDetail,
+    },
+)
+def create_reservation(
+    request: HttpRequest,
+    payload: ReserveInventoryIn,
+    idempotency_key: str = Header(...),
+) -> tuple[int, ReservationOut | ProblemDetail]:
+    result: ReserveInventoryResult = reserve_inventory(
+        sku=payload.sku,
+        quantity=payload.quantity,
+        idempotency_key=idempotency_key,
+    )
+
+    if result.code in {"reserved", "replayed"}:
+        status = 201 if result.code == "reserved" else 200
+        return status, ReservationOut(
+            id=result.reservation_id,
+            sku=result.sku,
+            quantity=result.quantity,
+        )
+
+    if result.code == "sku_not_found":
+        return 404, problem(404, "SKU Not Found", "Inventory item does not exist.", request.path)
+    if result.code == "insufficient_stock":
+        return 422, problem(422, "Insufficient Stock", "Not enough stock is available.", request.path)
+    return 409, problem(409, "Idempotency Conflict", "Idempotency key is already used differently or still processing.", request.path)
diff --git a/config/api.py b/config/api.py
new file mode 100644
--- /dev/null
+++ b/config/api.py
@@
+from ninja import NinjaAPI
+
+from inventory.api import router as inventory_router
+
+api = NinjaAPI()
+api.add_router("/inventory", inventory_router)
```

동시성 전략은 pessimistic locking입니다. 같은 SKU 예약은 `InventoryItem.objects.select_for_update()`로 한 트랜잭션 안에서 직렬화되어 oversell을 막습니다. 트래픽이 높고 충돌이 낮다면 `version` 필드를 사용해 `WHERE version = expected AND available_quantity >= quantity` 조건부 `UPDATE`를 수행하고 실패 시 재시도하는 optimistic locking으로 바꿀 수 있습니다.

검증은 read-only라 실행하지 않았습니다. 적용 후 실행할 명령은 다음입니다.

```bash
python manage.py makemigrations inventory
python manage.py check
pytest
```

---
> **관련 스킬 참조:**
> - Django Ninja API 구현 → **implementation-django-ninja** 스킬