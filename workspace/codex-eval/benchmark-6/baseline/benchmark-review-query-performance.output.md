**주요 내용**

지정된 fixture 경로 `/Users/hyun/Desktop/dddjango/none`는 없고, 평가 프롬프트에도 `Fixture: none`으로 되어 있어 실제 파일/라인 단위 리뷰는 불가능했습니다. 아래는 주문 목록 API에서 확인해야 할 핵심 findings입니다.

**Findings**

[QuerySet 최적화] -- 주문 목록 응답에서 `customer`, `payment`, `shipping_address` 같은 FK/O2O를 노출하면 `select_related()`가 필요합니다. `items`, `items.product` 같은 역방향 FK/M2M는 `prefetch_related()` 또는 `Prefetch(..., to_attr=...)`로 고정해야 합니다. Ninja Schema resolver가 `obj.items.all()`, `obj.customer.name`, `obj.items.count()`를 주문마다 호출하면 페이지 크기만큼 쿼리가 선형 증가합니다.

[Schema 분리] -- 목록 API가 상세 API와 같은 nested `ModelSchema`를 쓰면 직렬화 단계에서 lazy loading과 payload 비대화가 같이 발생합니다. `OrderListItemSchema`는 id, status, total, created_at, customer summary, item_count 정도로 얕게 두고, 품목 상세는 주문 상세 API로 분리하는 편이 안전합니다. `fields = "__all__"` 또는 과한 nested relation은 목록 응답에 부적합합니다.

[Pagination 전략] -- 큰 주문 테이블에서 offset/page-number pagination은 뒤 페이지로 갈수록 느려집니다. 최신순 주문 목록은 cursor/keyset pagination이 더 적합하고, 정렬은 `("-created_at", "-id")`처럼 stable tie-breaker가 필요합니다. `created_at` 단독 정렬은 같은 시각 주문에서 중복/누락 위험이 있습니다.

[응답 구조] -- Django Ninja에서 `@paginate`를 쓰면서 커스텀 `{items, meta}` envelope를 직접 반환하거나 `response=list[...]`와 envelope를 섞으면 응답 계약이 어긋납니다. 내장 paginator를 쓰면 paginator 형식을 따르고, 팀 표준 envelope가 필요하면 직접 slicing하거나 `PaginationBase`를 확장해야 합니다.

[Count 병목] -- 매 요청마다 `queryset.count()`로 `total`을 내려주면 대형 주문 테이블에서 병목이 됩니다. 무조건 총 개수가 필요한 화면이 아니라면 cursor의 `next` 중심 응답으로 바꾸고, total은 별도 endpoint/cache/근사값으로 분리하는 쪽을 검토해야 합니다.

[인덱스] -- “내 주문 최신순”, “상태별 최신순” 쿼리라면 `(user_id, -created_at, -id)` 또는 `(user_id, status, -created_at, -id)` 같은 복합 인덱스를 `EXPLAIN ANALYZE`로 검증해야 합니다. 단일 인덱스 여러 개가 WHERE + ORDER BY 조합을 항상 해결하지는 않습니다.

[테스트] -- N+1은 회귀가 쉽기 때문에 `assertNumQueries` 또는 `django_assert_num_queries`로 주문 1개와 50개일 때 쿼리 수가 선형 증가하지 않는지 고정해야 합니다. 목표 쿼리 수는 대략 주문 조회 1, prefetch 1~2, 인증/세션 등 프로젝트 공통 쿼리를 포함해 정하면 됩니다.

검증은 실행하지 못했습니다. 현재 작업 디렉터리는 비어 있고 sandbox가 read-only라 실제 endpoint 호출, SQL 확인, pytest 실행은 불가능했습니다.

---
> **관련 스킬 참조:**
> - Django ORM N+1 최적화 → **implementation-django** 스킬
> - Django Ninja 응답/페이지네이션 → **implementation-django-ninja** 스킬
> - Cursor/Keyset pagination 설계 → **architecture-api** 스킬