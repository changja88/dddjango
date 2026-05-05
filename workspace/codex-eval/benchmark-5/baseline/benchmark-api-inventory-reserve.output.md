지정된 fixture path `/Users/hyun/Desktop/dddjango/none`는 이 샌드박스에서 존재하지 않았고, 현재 작업 디렉터리도 비어 있었습니다. 그래서 기존 코드 스타일을 반영할 수는 없었고, Django Ninja 앱에 바로 얹을 수 있는 형태의 unified diff로 제안합니다.

```diff
diff --git a/inventory/models.py b/inventory/models.py
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/inventory/models.py
@@ -0,0 +1,52 @@
+from django.db import models
+
+
+class Stock(models.Model):
+    sku = models.CharField(max_length=64, unique=True)
+    available_quantity = models.PositiveIntegerField(default=0)
+    reserved_quantity = models.PositiveIntegerField(default=0)
+    updated_at = models.DateTimeField(auto_now=True)
+
+    def reserve(self, quantity: int) -> None:
+        if quantity <= 0:
+            raise ValueError("quantity must be positive")
+        if self.available_quantity < quantity:
+            raise ValueError("insufficient stock")
+
+        self.available_quantity -= quantity
+        self.reserved_quantity += quantity
+
+
+class Reservation(models.Model):
+    class Status(models.TextChoices):
+        COMPLETED = "completed", "Completed"
+
+    idempotency_key = models.CharField(max_length=128, unique=True)
+    request_hash = models.CharField(max_length=64)
+    sku = models.CharField(max_length=64)
+    quantity = models.PositiveIntegerField()
+    status = models.CharField(
+        max_length=32,
+        choices=Status.choices,
+        default=Status.COMPLETED,
+    )
+    created_at = models.DateTimeField(auto_now_add=True)
+
+    class Meta:
+        indexes = [
+            models.Index(fields=["sku"]),
+            models.Index(fields=["created_at"]),
+        ]
diff --git a/inventory/schemas.py b/inventory/schemas.py
new file mode 100644
index 0000000..2222222
--- /dev/null
+++ b/inventory/schemas.py
@@ -0,0 +1,24 @@
+from ninja import Schema
+
+
+class ReserveStockIn(Schema):
+    sku: str
+    quantity: int
+
+
+class ReservationOut(Schema):
+    reservation_id: int
+    sku: str
+    quantity: int
+    status: str
+
+
+class ErrorOut(Schema):
+    detail: str
diff --git a/inventory/api.py b/inventory/api.py
new file mode 100644
index 0000000..3333333
--- /dev/null
+++ b/inventory/api.py
@@ -0,0 +1,96 @@
+import hashlib
+import json
+
+from django.db import IntegrityError, transaction
+from ninja import Header, Router
+
+from .models import Reservation, Stock
+from .schemas import ErrorOut, ReservationOut, ReserveStockIn
+
+router = Router(tags=["inventory"])
+
+
+def make_request_hash(payload: ReserveStockIn) -> str:
+    raw = json.dumps(payload.dict(), sort_keys=True, separators=(",", ":"))
+    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
+
+
+def reservation_response(reservation: Reservation) -> dict:
+    return {
+        "reservation_id": reservation.id,
+        "sku": reservation.sku,
+        "quantity": reservation.quantity,
+        "status": reservation.status,
+    }
+
+
+def get_or_create_idempotency_row(
+    *,
+    idempotency_key: str,
+    request_hash: str,
+    payload: ReserveStockIn,
+) -> tuple[Reservation, bool]:
+    try:
+        reservation, created = Reservation.objects.get_or_create(
+            idempotency_key=idempotency_key,
+            defaults={
+                "request_hash": request_hash,
+                "sku": payload.sku,
+                "quantity": payload.quantity,
+            },
+        )
+    except IntegrityError:
+        created = False
+        reservation = Reservation.objects.get(idempotency_key=idempotency_key)
+
+    reservation = (
+        Reservation.objects.select_for_update()
+        .get(idempotency_key=reservation.idempotency_key)
+    )
+    return reservation, created
+
+
+@router.post(
+    "/reservations",
+    response={
+        201: ReservationOut,
+        200: ReservationOut,
+        400: ErrorOut,
+        404: ErrorOut,
+        409: ErrorOut,
+    },
+)
+def reserve_stock(
+    request,
+    payload: ReserveStockIn,
+    idempotency_key: str = Header(..., alias="Idempotency-Key"),
+):
+    if payload.quantity <= 0:
+        return 400, {"detail": "quantity must be positive"}
+
+    request_hash = make_request_hash(payload)
+
+    with transaction.atomic():
+        reservation, created = get_or_create_idempotency_row(
+            idempotency_key=idempotency_key,
+            request_hash=request_hash,
+            payload=payload,
+        )
+
+        if not created:
+            if reservation.request_hash != request_hash:
+                return 409, {
+                    "detail": "idempotency key was already used with a different request"
+                }
+            return 200, reservation_response(reservation)
+
+        stock = Stock.objects.select_for_update().filter(sku=payload.sku).first()
+        if stock is None:
+            reservation.delete()
+            return 404, {"detail": "stock not found"}
+
+        try:
+            stock.reserve(payload.quantity)
+        except ValueError as exc:
+            reservation.delete()
+            return 409, {"detail": str(exc)}
+
+        stock.save(update_fields=["available_quantity", "reserved_quantity", "updated_at"])
+
+    return 201, reservation_response(reservation)
diff --git a/project/api.py b/project/api.py
new file mode 100644
index 0000000..4444444
--- /dev/null
+++ b/project/api.py
@@ -0,0 +1,8 @@
+from ninja import NinjaAPI
+
+from inventory.api import router as inventory_router
+
+api = NinjaAPI()
+api.add_router("/inventory", inventory_router)
diff --git a/project/urls.py b/project/urls.py
new file mode 100644
index 0000000..5555555
--- /dev/null
+++ b/project/urls.py
@@ -0,0 +1,7 @@
+from django.urls import path
+
+from .api import api
+
+urlpatterns = [
+    path("api/", api.urls),
+]
```

핵심 설계는 다음입니다.

- 중복 요청 방지: `Reservation.idempotency_key`에 unique 제약.
- idempotency 처리: 같은 key + 같은 payload면 기존 예약을 `200`으로 반환, 같은 key + 다른 payload면 `409`.
- 동시성 처리: `transaction.atomic()` 안에서 `Reservation`과 `Stock`을 `select_for_update()`로 잠가 같은 SKU에 대한 동시 차감 경쟁을 직렬화.
- 재고 부족/없는 SKU 실패 시에는 선점한 idempotency row를 삭제해서 같은 key로 수정 후 재시도할 수 있게 했습니다.

실제 프로젝트에 적용할 때는 `inventory`를 `INSTALLED_APPS`에 추가하고 migration을 생성해야 합니다.