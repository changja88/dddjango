Fixture를 읽어보니 현재 조회/쓰기 패턴은 `Order` PK 조회, `select_for_update()` PK 조회, `Reservation` 생성 시 `idempotency_key` 저장입니다. 요청하신 개선 diff는 모델 `Meta`에 명시적 index/constraint를 두고, migration 예시를 추가하는 형태가 적절합니다.

```diff
diff --git a/shop/orders/models.py b/shop/orders/models.py
index 3a6f7a1..b4db9dd 100644
--- a/shop/orders/models.py
+++ b/shop/orders/models.py
@@ -16,6 +16,13 @@ class Order(models.Model):
     cancel_reason = models.TextField(blank=True)
     created_at = models.DateTimeField(auto_now_add=True)
 
+    class Meta:
+        indexes = [
+            models.Index(
+                fields=["status", "-created_at"],
+                name="orders_order_status_created_idx",
+            ),
+        ]
+
     def cancel(self, reason: str, actor_email: str) -> None:
         if self.status == self.STATUS_SHIPPED:
             raise ValueError("shipped orders cannot be cancelled")
@@ -44,3 +51,16 @@ class Reservation(models.Model):
     quantity = models.PositiveIntegerField()
     idempotency_key = models.CharField(max_length=128)
     created_at = models.DateTimeField(auto_now_add=True)
+
+    class Meta:
+        indexes = [
+            models.Index(
+                fields=["created_at"],
+                name="orders_reservation_created_idx",
+            ),
+        ]
+        constraints = [
+            models.UniqueConstraint(
+                fields=["idempotency_key"],
+                name="orders_reservation_idempotency_key_uniq",
+            ),
+        ]
diff --git a/shop/orders/migrations/__init__.py b/shop/orders/migrations/__init__.py
new file mode 100644
index 0000000..e69de29
diff --git a/shop/orders/migrations/0001_indexes_constraints.py b/shop/orders/migrations/0001_indexes_constraints.py
new file mode 100644
index 0000000..557f8f1
--- /dev/null
+++ b/shop/orders/migrations/0001_indexes_constraints.py
@@ -0,0 +1,33 @@
+from django.db import migrations, models
+
+
+class Migration(migrations.Migration):
+    dependencies = [
+        ("orders", "0001_initial"),
+    ]
+
+    operations = [
+        migrations.AddIndex(
+            model_name="order",
+            index=models.Index(
+                fields=["status", "-created_at"],
+                name="orders_order_status_created_idx",
+            ),
+        ),
+        migrations.AddIndex(
+            model_name="reservation",
+            index=models.Index(
+                fields=["created_at"],
+                name="orders_reservation_created_idx",
+            ),
+        ),
+        migrations.AddConstraint(
+            model_name="reservation",
+            constraint=models.UniqueConstraint(
+                fields=["idempotency_key"],
+                name="orders_reservation_idempotency_key_uniq",
+            ),
+        ),
+    ]
```

주의점: fixture에는 실제 `migrations/0001_initial.py`가 없어서 위 migration은 “기존 initial migration이 있는 프로젝트 기준 예시”입니다. 이 fixture에 그대로 넣는다면 `dependencies`를 실제 initial migration 이름에 맞추거나, 아예 initial migration을 생성해야 합니다.

또 하나 중요한 점은 현재 `reserve_inventory()`가 `Idempotency-Key` 누락 시 `""`를 저장합니다. 위 unique constraint를 적용하면 빈 키 예약은 한 번만 허용됩니다. 운영 코드라면 header 누락 시 `400`을 반환하거나, `idempotency_key`에 `blank=False`와 비어 있지 않다는 `CheckConstraint`까지 같이 두는 편이 더 안전합니다.