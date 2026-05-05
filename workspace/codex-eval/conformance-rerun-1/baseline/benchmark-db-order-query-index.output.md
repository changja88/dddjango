현재 작업 디렉터리에 코드가 없어 일반적인 Django ORM/Admin 주문 목록 기준으로 제안합니다.

**조회 패턴 먼저 확인**

관리자 주문 목록은 보통 아래 조건 조합이 병목입니다.

- 최신 주문순 정렬: `ORDER BY created_at DESC, id DESC`
- 상태 필터: `status`
- 기간 필터: `created_at__gte`, `created_at__lt`
- 결제/배송 상태 필터: `payment_status`, `shipping_status`
- 고객 검색: `user__email`, `user__name`, `phone`
- 상점/판매자별 필터: `store_id`, `seller_id`
- N+1: 주문 목록에서 고객, 결제, 배송지, 상품 요약을 같이 표시

**우선 검토할 인덱스**

PostgreSQL 기준 예시입니다.

```python
class Order(models.Model):
    ...

    class Meta:
        indexes = [
            models.Index(fields=["-created_at", "-id"], name="order_created_id_desc_idx"),
            models.Index(fields=["status", "-created_at", "-id"], name="order_status_created_idx"),
            models.Index(fields=["payment_status", "-created_at", "-id"], name="order_pay_created_idx"),
            models.Index(fields=["shipping_status", "-created_at", "-id"], name="order_ship_created_idx"),
            models.Index(fields=["user", "-created_at", "-id"], name="order_user_created_idx"),
        ]
```

멀티테넌트나 판매자별 관리자라면 가장 먼저 이쪽을 봅니다.

```python
models.Index(fields=["store", "-created_at", "-id"], name="order_store_created_idx")
models.Index(fields=["store", "status", "-created_at", "-id"], name="order_store_status_created_idx")
```

목록이 “최근 주문 + 특정 상태” 중심이면 단일 인덱스보다 복합 인덱스가 중요합니다. `WHERE status = ? ORDER BY created_at DESC LIMIT 50` 형태는 `["status", "-created_at", "-id"]`가 잘 맞습니다.

**검색 쿼리 개선**

`icontains`는 일반 B-tree 인덱스를 잘 못 탑니다.

```python
Order.objects.filter(user__email__icontains=q)
```

이런 검색이 많으면 PostgreSQL에서 trigram 인덱스를 검토합니다.

```python
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import TrigramExtension

class Migration(migrations.Migration):
    operations = [
        TrigramExtension(),
        migrations.AddIndex(
            model_name="user",
            index=GinIndex(
                fields=["email"],
                name="user_email_trgm_idx",
                opclasses=["gin_trgm_ops"],
            ),
        ),
    ]
```

주문번호처럼 prefix 검색이 가능하면 `icontains` 대신 `startswith` 계열로 바꾸는 것도 검토합니다.

```python
Order.objects.filter(order_number__startswith=q)
```

정확 일치 검색이 가능하면 가장 좋습니다.

```python
Order.objects.filter(order_number=q)
```

**ORM 쿼리 개선**

Admin 목록에서는 `get_queryset()`에서 관계 로딩을 명시하는 편이 좋습니다.

```python
class OrderAdmin(admin.ModelAdmin):
    list_select_related = ("user", "payment", "shipping_address")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return (
            qs.select_related("user", "payment", "shipping_address")
              .only(
                  "id",
                  "order_number",
                  "status",
                  "payment_status",
                  "created_at",
                  "total_price",
                  "user__id",
                  "user__email",
              )
        )
```

역참조나 M2M 상품 목록을 표시한다면 `prefetch_related()`를 쓰되, 관리자 목록에서 매 행마다 상품 전체를 렌더링하는 구조는 피하는 게 낫습니다. 필요하면 `Count`, `Sum`, `Exists`, `Subquery`로 요약값만 붙입니다.

```python
Order.objects.annotate(
    item_count=Count("items"),
)
```

다만 `Count`가 큰 조인과 결합되면 느려질 수 있으니 EXPLAIN으로 확인해야 합니다.

**Admin 자체 개선**

검토할 설정입니다.

```python
show_full_result_count = False
```

Django Admin은 페이지네이션에서 전체 건수 `COUNT(*)`가 병목이 되는 경우가 많습니다. 주문이 수백만 건이면 이 옵션만으로도 체감 차이가 큽니다.

또한 `list_display` 메서드에서 아래 패턴이 있으면 제거 대상입니다.

```python
def customer_email(self, obj):
    return obj.user.email  # select_related 없으면 N+1

def item_names(self, obj):
    return ", ".join(item.name for item in obj.items.all())  # 목록에서 위험
```

**Migration 검증**

인덱스 추가 전후로 아래를 확인합니다.

```bash
python manage.py makemigrations --check --dry-run
python manage.py sqlmigrate orders 000X
python manage.py migrate --plan
```

PostgreSQL 운영 DB라면 큰 테이블에는 일반 `CREATE INDEX`가 락 부담이 있을 수 있습니다. 필요하면 `CREATE INDEX CONCURRENTLY`를 별도 migration으로 검토합니다.

```python
class Migration(migrations.Migration):
    atomic = False

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS order_status_created_idx
            ON orders_order (status, created_at DESC, id DESC);
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS order_status_created_idx;
            """,
        )
    ]
```

Django의 `AddIndex`는 DB와 버전에 따라 concurrent 생성이 아니므로 운영 대용량 테이블에서는 주의해야 합니다.

**EXPLAIN 기준**

Django에서 직접 확인합니다.

```python
qs = (
    Order.objects
    .filter(status="paid", created_at__gte=start, created_at__lt=end)
    .order_by("-created_at", "-id")
    .select_related("user")
)

print(qs.explain(analyze=True, buffers=True))
```

봐야 할 기준은 다음입니다.

- `Seq Scan`이 큰 주문 테이블에서 발생하지 않는지
- `Index Scan`, `Index Only Scan`, `Bitmap Index Scan`이 쓰이는지
- `Sort`가 크게 발생하지 않는지
  정렬 인덱스가 맞으면 별도 대형 sort가 줄어야 합니다.
- `Rows Removed by Filter`가 과도하지 않은지
- 예상 rows와 실제 rows 차이가 큰지
- `LIMIT 50`인데 수십만 row를 훑고 있지 않은지
- `shared read blocks`가 과도한지
- Admin 목록 한 페이지 로딩 시 쿼리 수가 N+1로 증가하지 않는지

핵심은 “필터 조건 + 정렬 + 페이지 크기”를 하나의 실제 목록 쿼리로 보고, 그 쿼리에 맞는 복합 인덱스를 최소 개수로 추가하는 것입니다. 보통 첫 후보는 `("-created_at", "-id")`, 그다음은 자주 쓰는 필터를 앞에 둔 `("status", "-created_at", "-id")` 계열입니다.