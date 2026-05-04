현재 `/private/tmp/dddjango-codex-eval`에는 프로젝트 파일이 없어서 실제 모델/쿼리는 확인하지 못했습니다. Django 관리자 주문 목록이 느릴 때는 보통 아래를 우선 검토합니다.

**인덱스 후보**

1. 목록 정렬 기준
   ```python
   class Order(models.Model):
       created_at = models.DateTimeField(db_index=True)
   ```
   관리자 목록이 `-created_at`, `-id` 등으로 정렬된다면 해당 컬럼 인덱스가 필요합니다.

2. 상태 필터
   ```python
   status = models.CharField(max_length=20, db_index=True)
   ```
   `list_filter = ("status", ...)`처럼 자주 거는 필터는 인덱스 후보입니다.

3. 결합 조건
   ```python
   class Meta:
       indexes = [
           models.Index(fields=["status", "-created_at"]),
           models.Index(fields=["customer", "-created_at"]),
           models.Index(fields=["payment_status", "-created_at"]),
       ]
   ```
   관리자 화면에서 “상태별 최신 주문”처럼 조회한다면 단일 인덱스보다 복합 인덱스가 더 효과적일 수 있습니다.

4. 검색 대상
   `search_fields = ("order_number", "customer__email")`라면:
   ```python
   order_number = models.CharField(max_length=64, db_index=True)
   ```
   단, `icontains` 검색은 일반 B-tree 인덱스를 잘 못 씁니다. PostgreSQL이면 `pg_trgm` 기반 `GinIndex`도 검토합니다.

5. 날짜 범위 필터
   ```python
   models.Index(fields=["created_at"])
   ```
   `created_at__gte`, `created_at__lte`가 많으면 필수 후보입니다.

**Django Admin 쿼리 개선**

1. `select_related` 사용  
   주문 목록에서 고객, 결제, 배송지 같은 FK를 표시한다면 N+1이 흔합니다.

   ```python
   @admin.register(Order)
   class OrderAdmin(admin.ModelAdmin):
       list_display = ("id", "customer", "status", "total_price", "created_at")
       list_select_related = ("customer", "payment")
   ```

   또는:

   ```python
   def get_queryset(self, request):
       qs = super().get_queryset(request)
       return qs.select_related("customer", "payment")
   ```

2. M2M / reverse 관계는 `prefetch_related`

   ```python
   def get_queryset(self, request):
       qs = super().get_queryset(request)
       return qs.select_related("customer").prefetch_related("items")
   ```

3. `list_display`에서 무거운 메서드 제거  
   예를 들어 각 행마다 이런 코드가 있으면 느립니다.

   ```python
   def item_count(self, obj):
       return obj.items.count()
   ```

   대신 annotate:

   ```python
   from django.db.models import Count

   def get_queryset(self, request):
       return super().get_queryset(request).annotate(item_count=Count("items"))

   def item_count(self, obj):
       return obj.item_count
   ```

4. 관리자 검색 범위 축소  
   `search_fields`에 관계 필드가 많으면 JOIN + LIKE 검색으로 급격히 느려집니다.

   ```python
   search_fields = ("id", "order_number", "customer__email")
   ```

   가능하면 주문번호, 이메일처럼 실제 운영자가 많이 쓰는 필드만 남기는 게 좋습니다.

5. 전체 카운트 비용 줄이기  
   주문 수가 많으면 admin pagination의 `COUNT(*)`도 병목이 됩니다.

   ```python
   show_full_result_count = False
   ```

6. 기본 정렬 확인

   ```python
   ordering = ("-created_at",)
   ```

   여기에 맞춰 `created_at` 또는 `("-created_at", "id")` 계열 인덱스를 검토합니다.

우선순위는 `EXPLAIN ANALYZE`로 실제 admin 쿼리를 확인한 뒤, `WHERE`, `ORDER BY`, `JOIN`에 반복적으로 등장하는 컬럼부터 잡는 것이 좋습니다. 실무적으로는 `list_select_related`, 무거운 `list_display` 제거, `status + created_at` 복합 인덱스가 가장 먼저 효과를 내는 경우가 많습니다.