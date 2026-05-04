**[주요 내용]**

관리자 주문 목록이 느릴 때는 먼저 “관리자가 실제로 자주 쓰는 필터 + 정렬” 조합을 기준으로 봐야 합니다. 인덱스는 컬럼별로 많이 추가하는 게 아니라, 대표 쿼리 2~4개를 정하고 그 쿼리의 `WHERE`와 `ORDER BY`를 맞추는 방식이 좋습니다.

예를 들어 주문 목록이 보통 아래처럼 조회된다고 가정합니다.

```python
Order.objects.filter(
    status="paid",
    payment_status="completed",
    created_at__gte=start,
    created_at__lt=end,
).order_by("-created_at", "-id")
```

이 경우 우선 검토할 복합 인덱스는 동등 조건 → 범위/정렬 조건 순서입니다.

```python
class Order(models.Model):
    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "status",
                    "payment_status",
                    "-created_at",
                    "-id",
                ],
                name="order_status_pay_created_id_idx",
            ),
        ]
```

관리자에서 판매자/스토어별 주문을 자주 본다면 별도 패턴입니다.

```python
Order.objects.filter(
    store_id=store_id,
    created_at__gte=start,
    created_at__lt=end,
).order_by("-created_at", "-id")
```

```python
models.Index(
    fields=["store", "-created_at", "-id"],
    name="order_store_created_id_idx",
)
```

고객별 주문 조회가 많으면 다음도 후보입니다.

```python
models.Index(
    fields=["customer", "-created_at", "-id"],
    name="order_customer_created_id_idx",
)
```

단, `status` 단독 인덱스처럼 카디널리티가 낮은 컬럼 하나만 인덱싱하는 것은 보통 효과가 작습니다. `status + created_at 정렬`, `store + created_at 정렬`처럼 실제 목록 조회 패턴과 결합될 때 의미가 있습니다.

삭제/취소/완료 상태 중 “최근 처리 대상”만 자주 본다면 PostgreSQL에서는 partial index도 검토할 수 있습니다.

```python
models.Index(
    fields=["-created_at", "-id"],
    name="order_open_created_id_idx",
    condition=models.Q(status__in=["paid", "preparing", "shipping"]),
)
```

검색 조건은 별도로 봐야 합니다. `order_number = ...` 같은 exact lookup은 B-tree 인덱스가 잘 맞습니다.

```python
models.Index(fields=["order_number"], name="order_number_idx")
```

반면 `customer_name__icontains`, `memo__icontains` 같은 부분 문자열 검색은 일반 B-tree 인덱스로 해결되지 않습니다. PostgreSQL이면 `pg_trgm` 기반 `GinIndex`를 검토하거나, 관리자 검색 필드를 exact/prefix 중심으로 제한하는 편이 낫습니다.

Django admin 쿼리 쪽은 다음을 같이 봅니다.

```python
class OrderAdmin(admin.ModelAdmin):
    list_select_related = ("customer", "store", "payment")
    list_per_page = 50
    show_full_result_count = False
```

`select_related()`는 `customer`, `store`, `payment`처럼 FK/O2O를 목록에 표시할 때 N+1을 줄입니다. 하지만 필터/정렬 자체를 빠르게 하지는 않습니다. 즉, `select_related`는 “행을 가져온 뒤 관련 객체를 추가 조회하는 비용”을 줄이고, 인덱스는 “대상 주문 행을 찾고 정렬하는 비용”을 줄입니다.

`prefetch_related()`는 M2M 또는 reverse FK에 사용합니다. 주문 목록에서 주문상품 라인까지 표시한다면 다음처럼 페이지를 먼저 자른 뒤 prefetch되도록 해야 합니다.

```python
qs = (
    Order.objects.filter(...)
    .select_related("customer", "store")
    .order_by("-created_at", "-id")
)

page = qs[:50]

page = page.prefetch_related(
    Prefetch("items", queryset=OrderItem.objects.select_related("product"))
)
```

`prefetch_related()`는 별도 쿼리로 관련 데이터를 묶어 가져옵니다. 페이지 크기가 50이면 괜찮을 수 있지만, offset이 큰 페이지에서 `OFFSET 50000 LIMIT 50` 자체가 이미 비쌉니다. 느린 원인이 pagination이면 인덱스를 추가해도 한계가 있습니다.

큰 페이지 번호 접근이 많으면 offset pagination 대신 keyset pagination을 검토합니다.

```python
Order.objects.filter(
    created_at__lt=last_created_at,
).order_by("-created_at", "-id")[:50]
```

동일한 `created_at` 값이 있을 수 있으므로 실제로는 `created_at`, `id`를 함께 cursor로 써야 합니다.

검증 기준은 이 정도로 잡는 게 좋습니다.

```bash
python manage.py shell
```

```python
qs = Order.objects.filter(...).order_by("-created_at", "-id")
print(qs.explain(analyze=True, buffers=True))
```

확인할 지표는 `Seq Scan` 여부, `Sort`가 크게 발생하는지, `actual time`, `rows`, `Rows Removed by Filter`, `Buffers`, `Heap Fetches`입니다. Django 레벨에서는 관리자 목록 렌더링 쿼리 수를 `assertNumQueries` 또는 Django Debug Toolbar로 확인합니다.

추가 판단 기준은 명확히 두는 편이 좋습니다.

- P95 관리자 목록 응답 시간이 목표보다 느린가
- 대표 필터 조합에서 `EXPLAIN ANALYZE`가 Seq Scan 또는 큰 Sort를 보이는가
- 인덱스 추가 후 쓰기 비용 증가가 감당 가능한가
- 같은 역할의 복합 인덱스가 이미 존재하지 않는가
- `select_related/prefetch_related` 문제인지, 필터/정렬/pagination 문제인지 분리했는가

우선순위는 `EXPLAIN ANALYZE`로 느린 대표 쿼리 확정 → 복합 인덱스 1~2개 추가 → admin N+1 제거 → count/offset pagination 비용 완화 순서가 적절합니다.

---
> **관련 스킬 참조:**
> - DB 인덱스/쿼리 실행계획 검토 → **architecture-db** 스킬
> - Django ORM/Admin QuerySet 최적화 → **implementation-django** 스킬