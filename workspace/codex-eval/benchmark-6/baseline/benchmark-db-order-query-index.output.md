Fixture path `/Users/hyun/Desktop/dddjango/none`는 현재 환경에서 존재하지 않고, 작업 디렉터리 `/private/tmp/dddjango-codex-eval`도 비어 있어 실제 모델/쿼리는 확인할 수 없었습니다. 그래서 특정 파일 diff 대신 Django ORM 기준으로 관리자 주문 목록이 느릴 때 검토할 항목을 정리합니다.

**우선 확인할 쿼리**

관리자 주문 목록에서 보통 병목은 다음 조합입니다.

```python
Order.objects
    .select_related("user", "status", "payment")
    .prefetch_related("items", "items__product")
    .filter(...)
    .order_by("-created_at")
```

Django Admin이라면 `ModelAdmin`에서 다음을 먼저 확인합니다.

```python
class OrderAdmin(admin.ModelAdmin):
    list_select_related = ("user", "status", "payment")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user", "status", "payment")
```

`list_display`에서 `obj.user.email`, `obj.payment.method`, `obj.items.count()` 같은 접근이 있다면 N+1 또는 반복 COUNT가 날 수 있습니다. `items.count()`는 `annotate()`로 빼는 편이 낫습니다.

```python
from django.db.models import Count

def get_queryset(self, request):
    return (
        super()
        .get_queryset(request)
        .select_related("user", "status", "payment")
        .annotate(item_count=Count("items"))
    )
```

**검토할 인덱스**

주문 목록은 대개 최신순 정렬과 상태/기간/고객 검색이 핵심이라 아래 인덱스를 우선 검토합니다.

```python
class Order(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["payment_status", "-created_at"]),
            models.Index(fields=["is_deleted", "-created_at"]),
        ]
```

자주 쓰는 필터 조합이 `상태 + 기간 + 최신순`이면 단일 인덱스 여러 개보다 복합 인덱스가 효과적입니다.

```python
models.Index(fields=["status", "-created_at"])
```

관리자 검색이 `order_number` 정확 검색이면 일반 B-tree 인덱스 또는 unique 인덱스를 둡니다.

```python
order_number = models.CharField(max_length=50, unique=True)
```

이메일/전화번호 부분 검색처럼 `icontains`가 많다면 일반 인덱스는 효과가 제한적입니다. PostgreSQL이면 `pg_trgm` 기반 trigram index를 검토합니다.

```python
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import TrigramSimilarity
```

**쿼리 개선 포인트**

`select_related()`는 FK/OneToOne에 사용합니다.

```python
.select_related("user", "shipping_address", "payment")
```

`prefetch_related()`는 M2M/reverse FK에 사용합니다.

```python
.prefetch_related("items", "items__product")
```

목록에서 필요 없는 큰 컬럼이 있다면 `defer()`도 검토합니다.

```python
.defer("memo", "raw_payload", "internal_note")
```

Django Admin의 `search_fields`가 너무 넓으면 줄이는 게 좋습니다. 특히 여러 related field에 `icontains`가 걸리면 느려집니다.

```python
search_fields = ("=order_number", "^user__email")
```

`=field`는 정확 검색, `^field`는 prefix 검색이라 무차별 `icontains`보다 인덱스를 활용하기 쉽습니다.

**확인 순서**

1. Django Debug Toolbar 또는 `QuerySet.explain()`으로 실제 SQL과 실행 계획 확인
2. `list_display`, `list_filter`, `search_fields`, `ordering`에서 발생하는 쿼리 확인
3. N+1이면 `select_related` / `prefetch_related` 적용
4. 정렬/필터 조건 기준으로 복합 인덱스 추가
5. `icontains` 검색은 정확/prefix 검색으로 바꾸거나 PostgreSQL trigram index 검토

실제 모델과 Admin 코드가 있으면 가장 좋은 답은 “현재 쿼리의 `WHERE + ORDER BY` 조합에 맞춘 최소 복합 인덱스”를 고르는 것입니다. 지금은 fixture가 없어 일반 제안까지만 가능합니다.