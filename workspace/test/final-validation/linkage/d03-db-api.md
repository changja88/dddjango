# d03-db-api: DB 스키마 완료 후 API 페이지네이션/필터링 설계

> **스킬 위임 경로:** architecture-db --> architecture-api (설계 모드)
>
> DB 스키마가 확정된 상태에서 API 응답의 페이지네이션과 필터링 설계를 요청받았다. architecture-db 스킬은 "REST API 설계 원칙(엔드포인트, 페이지네이션, 상태 코드)에 대해서는 architecture-api에 위임한다"고 명시하므로, architecture-api 스킬의 설계 모드로 응답한다.

---

## 페이지네이션 설계

### 방식 선택 기준

| 상황 | 권장 방식 | 이유 |
|------|----------|------|
| 소규모 데이터, 관리자 대시보드 | Offset (`?limit=25&offset=50`) | 단순하고 페이지 번호 제공 가능 |
| 실시간 피드, 무한 스크롤, 대용량 | Cursor (`?limit=25&starting_after=obj_abc`) | 일관성 + 성능 (100만 건에서 offset 대비 17배 빠름) |
| 고성능 읽기 중심 API | Keyset (`?limit=25&after_id=123`) | 인덱스 활용으로 일정한 O(1) 성능 |

대부분의 사용자향 API에는 **Cursor 기반 페이지네이션**을 기본으로 권장한다. Offset은 대규모 데이터에서 `OFFSET N`이 N개 행을 스캔 후 버리므로 성능이 선형적으로 저하된다.

### Cursor 페이지네이션 설계 원칙

1. **커서 필드 선택**: 인덱싱된, 불변, 유니크한 필드를 사용한다. 단일 필드가 유니크하지 않으면 `(created_at, id)` 조합을 사용한다.
2. **불투명 인코딩**: 커서 값을 base64로 인코딩하여 클라이언트가 토큰으로만 취급하도록 한다. 내부 구조 노출을 방지한다.
3. **페이지 크기 제한**: 기본값 25, 최대 100-200. `limit` 파라미터로 클라이언트가 조절 가능하되 상한을 강제한다.
4. **응답에 탐색 메타 포함**: `has_more`와 `next_cursor`를 반드시 포함한다.

### 요청/응답 예시

```
GET /orders?limit=25&cursor=eyJjcmVhdGVkX2F0IjoiMjAyNi0wNC0wNSIsImlkIjo0Mn0=
```

```json
{
  "data": [
    {"id": 43, "status": "shipped", "total": 15000, "created_at": "2026-04-05T10:30:00Z"},
    {"id": 44, "status": "pending", "total": 8500, "created_at": "2026-04-05T11:00:00Z"}
  ],
  "pagination": {
    "has_more": true,
    "next_cursor": "eyJjcmVhdGVkX2F0IjoiMjAyNi0wNC0wNSIsImlkIjo2N30="
  }
}
```

### DB 인덱스 연계

커서 페이지네이션이 효과적이려면 커서 필드에 대한 인덱스가 필수다. `ORDER BY created_at DESC, id DESC` 쿼리를 지원하는 복합 인덱스를 설계한다.

```sql
CREATE INDEX idx_orders_cursor ON orders (created_at DESC, id DESC);
```

등호 조건(필터)과 함께 사용할 경우, 필터 컬럼을 앞에 배치한다.

```sql
-- WHERE status = 'shipped' ORDER BY created_at DESC, id DESC
CREATE INDEX idx_orders_status_cursor ON orders (status, created_at DESC, id DESC);
```

---

## 필터링 설계

### 쿼리 파라미터 패턴

필터링, 정렬, 검색은 모두 쿼리 파라미터를 통해 처리한다. URL 경로에는 리소스 식별만 담는다.

```
GET /orders?status=shipped&min_total=10000          # 필터링
GET /orders?sort=-created_at,total                   # 정렬 (- = DESC)
GET /orders?fields=id,status,total                   # 필드 선택
GET /orders?q=keyboard                               # 전문 검색
GET /orders?price=gte:10000&price=lte:50000          # 범위 필터
```

### 설계 원칙

1. **허용된 필터만 적용**: 클라이언트가 보낸 임의의 필드를 그대로 WHERE 절에 넣지 않는다. 화이트리스트 방식으로 허용된 필터 필드를 명시한다.
2. **필터 가능한 필드에는 인덱스 보장**: 필터로 노출하는 필드는 반드시 DB에 인덱스가 존재해야 한다. 인덱스 없이 필터를 제공하면 대규모 테이블에서 Seq Scan이 발생한다.
3. **범위 필터 표현**: `gte:`, `lte:`, `gt:`, `lt:` 접두사를 사용하거나, `min_`/`max_` 접두사 파라미터를 사용한다. 프로젝트 내에서 하나의 방식으로 통일한다.
4. **정렬 기본값 명시**: 정렬 파라미터가 없을 때의 기본 정렬 순서를 문서화한다. 보통 `-created_at`(최신순)이 자연스럽다.
5. **필터와 페이지네이션 조합**: 필터 조건이 변경되면 커서를 초기화해야 한다. 이전 커서는 다른 필터 결과셋의 위치를 가리키므로 유효하지 않다.

### 필터링 + 페이지네이션 조합 예시

```
GET /orders?status=shipped&sort=-created_at&limit=25
GET /orders?status=shipped&sort=-created_at&limit=25&cursor=eyJjcmV...
```

### 잘못된 필터 파라미터에 대한 오류 응답

인식할 수 없는 필터 파라미터는 무시하거나 400 Bad Request를 반환한다. 엄격한 방식(400)이 클라이언트 실수를 빠르게 발견하게 하므로 권장한다. 오류 형식은 RFC 9457 Problem Details를 따른다.

```json
HTTP/1.1 400 Bad Request
Content-Type: application/problem+json

{
  "type": "https://api.example.com/problems/invalid-filter",
  "title": "Invalid filter parameter.",
  "status": 400,
  "detail": "Filter parameter 'colour' is not supported. Supported filters: status, min_total, max_total, created_after, created_before.",
  "instance": "/orders?colour=red"
}
```

---

> **관련 스킬 참조:**
> - DB 인덱스 설계와 쿼리 최적화 (커버링 인덱스, 복합 인덱스 순서) --> **architecture-db** 스킬
> - Django Ninja에서 페이지네이션/필터링 구현 (Schema, Router, QuerySet) --> **implementation-django-ninja** 스킬
> - 도메인 모델과 애그리거트 경계가 API 리소스 구조에 미치는 영향 --> **architecture-ddd** 스킬
