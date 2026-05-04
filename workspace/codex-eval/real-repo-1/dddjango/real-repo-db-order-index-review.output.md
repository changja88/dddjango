**[주요 내용]**

fixture에서 확인한 조회는 `Order.objects.get(id=...)`, `Product.objects.select_for_update().get(id=...)`, `Order.objects.select_for_update().get(id=...)`처럼 PK 기반이라 추가 인덱스가 필요 없습니다. 요청된 주문 목록성 조회에는 `status = ?` 동등 조건 뒤 `created_at` 정렬/범위가 붙는 패턴을 기준으로 `(status, -created_at)` 복합 인덱스가 맞습니다. 예약은 `idempotency_key`로 중복 생성을 막는 DB 제약이 핵심이고, 이 unique 제약 자체가 조회 인덱스 역할도 합니다.

```diff
diff --git a/shop/orders/models.py b/shop/orders/models.py
index 7c31f87..3c4b8a1 100644
--- a/shop/orders/models.py
+++ b/shop/orders/models.py
@@ -17,6 +17,14 @@ class Order(models.Model):
     cancel_reason = models.TextField(blank=True)
     created_at = models.DateTimeField(auto_now_add=True)
 
+    class Meta:
+        indexes = [
+            models.Index(
+                fields=["status", "-created_at"],
+                name="order_status_created_idx",
+            ),
+        ]
+
     def cancel(self, reason: str, actor_email: str) -> None:
         if self.status == self.STATUS_SHIPPED:
             raise ValueError("shipped orders cannot be cancelled")
@@ -44,3 +52,11 @@ class Reservation(models.Model):
     quantity = models.PositiveIntegerField()
     idempotency_key = models.CharField(max_length=128)
     created_at = models.DateTimeField(auto_now_add=True)
+
+    class Meta:
+        constraints = [
+            models.UniqueConstraint(
+                fields=["idempotency_key"],
+                name="reservation_idempo_key_uniq",
+            ),
+        ]
diff --git a/shop/orders/migrations/0002_indexes_constraints.py b/shop/orders/migrations/0002_indexes_constraints.py
new file mode 100644
index 0000000..b188aa1
--- /dev/null
+++ b/shop/orders/migrations/0002_indexes_constraints.py
@@ -0,0 +1,29 @@
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
+                name="order_status_created_idx",
+            ),
+        ),
+        migrations.AddConstraint(
+            model_name="reservation",
+            constraint=models.UniqueConstraint(
+                fields=["idempotency_key"],
+                name="reservation_idempo_key_uniq",
+            ),
+        ),
+    ]
```

근거:
- `id` 조회와 `select_for_update().get(id=...)`는 PK 인덱스를 이미 사용하므로 중복 인덱스가 필요 없습니다.
- `(status, -created_at)`는 `WHERE status = ... ORDER BY created_at DESC` 또는 `status + created_at range`에 맞습니다. 동등 조건 컬럼을 앞에 두고 범위/정렬 컬럼을 뒤에 둡니다.
- `Reservation.idempotency_key` unique는 동시 요청이 같은 키로 두 번 insert되는 것을 DB에서 차단합니다. 현재 뷰는 `Reservation.objects.create()`만 하므로, 적용 후에는 중복 키에서 `IntegrityError`를 잡아 기존 예약을 반환하도록 애플리케이션 코드도 맞추는 것이 좋습니다.
- transaction/locking 영향: 기존 `select_for_update()`는 `Product`, `Order` 행만 잠급니다. unique 제약은 `Reservation` insert 시 unique index 경합을 만들고, 같은 `idempotency_key` 동시 insert 중 하나를 실패시킵니다. 인덱스/제약 추가 마이그레이션은 테이블 락과 쓰기 지연이 생길 수 있어 큰 테이블이면 PostgreSQL concurrent index/별도 제약 검증 단계로 분리하세요.

검증 단계:

```bash
python manage.py makemigrations --check --dry-run
python manage.py sqlmigrate orders 0002
python manage.py test shop.orders
```

기존 데이터가 있다면 마이그레이션 전에 중복 키를 확인하세요.

```sql
SELECT idempotency_key, COUNT(*)
FROM orders_reservation
GROUP BY idempotency_key
HAVING COUNT(*) > 1;
```

---
> **관련 스킬 참조:**
> - migration rollout / concurrent index 적용 → **implementation-django** 스킬