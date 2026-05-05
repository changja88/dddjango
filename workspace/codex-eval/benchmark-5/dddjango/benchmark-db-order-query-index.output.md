**주요 내용**

지정 fixture path `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고, 현재 워크스페이스에도 fixture/source 파일이 없었습니다. 그래서 아래는 특정 파일 diff가 아니라, Django 관리자 주문 목록에서 검토할 **리뷰 findings + 적용 예시**입니다.

1. `[Index: 조회 조건 + 정렬 순서 기준] -- status/date/order_by 패턴에 맞는 복합 인덱스부터 검토`

관리자 주문 목록이 보통 아래처럼 조회된다면:

```python
Order.objects.filter(status=status).order_by("-created_at", "-id")
```

검토할 1순위 인덱스는 단일 `status`, 단일 `created_at`가 아니라 복합 인덱스입니다.

```python
class Meta:
    indexes = [
        models.Index(
            fields=["status", "-created_at", "-id"],
            name="order_status_created_id_idx",
        ),
    ]
```

이유: `status = ?`는 동등 조건이고, `created_at DESC, id DESC`는 정렬/페이지네이션 조건입니다. 동등 조건을 앞에 두고 정렬 컬럼을 뒤에 둬야 최신 주문 목록에서 sort 비용을 줄일 수 있습니다.

2. `[Index: 조합 필터는 실제 사용 빈도 확인] -- payment_status까지 항상 같이 필터링될 때만 확장`

아래 쿼리가 관리자에서 자주 쓰인다면:

```python
Order.objects.filter(
    status=status,
    payment_status=payment_status,
).order_by("-created_at", "-id")
```

후보는 다음입니다.

```python
models.Index(
    fields=["status", "payment_status", "-created_at", "-id"],
    name="order_status_pay_created_id_idx",
)
```

다만 `status`, `payment_status`, `created_at` 조합을 전부 만들면 쓰기 비용과 저장 공간이 증가합니다. 다음 기준으로 하나만 우선 검토하세요.

- `status` 단독 필터가 대부분: `["status", "-created_at", "-id"]`
- `status + payment_status` 조합이 대부분: `["status", "payment_status", "-created_at", "-id"]`
- `payment_status` 단독 필터도 독립적으로 많음: 별도 인덱스 후보로 측정

3. `[Index: 기간 필터] -- created_at range는 동등 조건 뒤에 둔다`

```python
Order.objects.filter(
    status=status,
    created_at__gte=start,
    created_at__lt=end,
).order_by("-created_at", "-id")
```

이 경우도 후보는 동일하게:

```python
models.Index(
    fields=["status", "-created_at", "-id"],
    name="order_status_created_id_idx",
)
```

범위 조건인 `created_at`을 `status`보다 앞에 두면 `status` 필터 활용도가 떨어질 수 있습니다.

4. `[Index: FK 인덱스와 복합 인덱스 구분] -- customer_id 단일 FK 인덱스만으로는 고객별 최신 주문 정렬이 부족할 수 있음`

Django FK는 기본적으로 `customer_id` 인덱스를 만듭니다. 하지만 아래 쿼리에는 복합 인덱스가 더 적합할 수 있습니다.

```python
Order.objects.filter(customer_id=customer_id).order_by("-created_at", "-id")
```

```python
models.Index(
    fields=["customer", "-created_at", "-id"],
    name="order_customer_created_id_idx",
)
```

5. `[QuerySet: select_related와 prefetch_related 비용 분리] -- JOIN 최적화와 페이지네이션 최적화는 다른 문제`

관리자 목록에서 FK/O2O 필드를 표시한다면 `select_related`를 사용합니다.

```python
qs = (
    Order.objects
    .select_related("customer", "payment")
    .order_by("-created_at", "-id")
)
```

역방향 FK/M2M, 예를 들어 주문 상품 목록을 표시한다면 `prefetch_related` 대상입니다.

```python
qs = Order.objects.prefetch_related("items")
```

다만 목록 페이지에서 `items` 전체를 보여주지 않고 개수만 필요하면 prefetch보다 `annotate()`가 낫습니다.

```python
qs = Order.objects.annotate(item_count=Count("items"))
```

중요한 구분은 이렇습니다.

- `select_related`: N+1 제거용 JOIN. 페이지 수가 작아도 효과 있음.
- `prefetch_related`: 별도 쿼리로 관련 객체를 모음. 페이지 크기만큼만 붙이면 유리하지만, 큰 페이지/무거운 related rows에서는 메모리 비용 증가.
- pagination: `COUNT(*)`, 큰 `OFFSET`, 정렬 sort 비용이 핵심. `select_related/prefetch_related`만으로 해결되지 않음.

6. `[Pagination: 큰 OFFSET 비용] -- 관리자 목록 후반 페이지가 느리면 keyset pagination 또는 admin count 비용을 검토`

기본 Django admin pagination은 후반 페이지에서 `OFFSET` 비용이 커질 수 있고, 전체 건수 `COUNT(*)`도 비쌀 수 있습니다. 관리자에서 정확한 전체 페이지 수가 덜 중요하다면 `show_full_result_count = False`를 먼저 검토합니다.

```python
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_select_related = ("customer", "payment")
    ordering = ("-created_at", "-id")
    show_full_result_count = False
```

7. `[Verification: 측정 기준] -- 인덱스 추가 전후 EXPLAIN으로 판단`

인덱스는 많이 추가하지 말고 아래 기준을 통과할 때만 추가하세요.

```python
qs.explain(analyze=True, buffers=True)
```

확인할 항목:

- 대형 `Seq Scan`이 `Index Scan`, `Bitmap Index Scan`, 가능하면 `Index Only Scan`으로 바뀌는지
- `Sort` 비용이 줄거나 사라지는지
- `actual rows`와 `estimated rows` 차이가 큰 경우 `ANALYZE` 후 재측정
- p95/p99 관리자 목록 응답 시간이 개선되는지
- 주문 생성/상태 변경 같은 write 경로가 느려지지 않는지
- 테스트에는 목록 표시 경로에 `assertNumQueries`를 추가해 N+1 회귀를 막는지

---
> **관련 스킬 참조:**
> - Django ORM QuerySet 최적화와 admin 조회 개선 → **implementation-django** 스킬
> - 복합 인덱스, 부분 인덱스, EXPLAIN ANALYZE 기반 검증 → **architecture-db** 스킬