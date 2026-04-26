# D15: architecture-api -> architecture-db 크로스 스킬 위임 테스트

## Prompt

"API 응답 성능이 느린데, DB 쿼리 최적화랑 인덱싱 전략을 같이 봐야 할 것 같아. 어떻게 접근해?"

## Skill Used

- **Primary:** architecture-api (설계 모드)
- **Delegated:** architecture-db (인덱스와 성능, 쿼리 최적화)

## Response

API 응답 성능 문제는 API 계층과 DB 계층을 함께 진단해야 한다. 각 계층에서의 접근법을 정리한다.

### 1단계: API 계층 진단

성능 병목이 API 설계 자체에서 오는지 먼저 확인한다.

**페이지네이션 패턴 점검.** 목록 엔드포인트가 제한 없이 전체 데이터를 반환하고 있다면, 이것만으로도 심각한 성능 저하 원인이 된다. 대용량 데이터(1M+ 레코드)에서는 Offset 기반 페이지네이션이 Cursor 기반보다 17배 느리다. 무한 스크롤이나 실시간 피드에는 Cursor 방식을 적용한다.

```
-- Offset: 뒤로 갈수록 느려짐
GET /v1/orders?limit=25&offset=100000

-- Cursor: 항상 일정한 성능
GET /v1/orders?limit=25&starting_after=ord_abc123
```

**응답 페이로드 점검.** SELECT * 로 불필요한 필드까지 전부 내려보내고 있다면, 필요한 필드만 반환하도록 수정한다. 이는 DB 커버링 인덱스 활용과도 직결된다.

**Rate Limiting 검토.** 비용이 큰 DB 작업을 수행하는 엔드포인트에는 반드시 rate limit 검사를 DB 쿼리 전에 배치하여 불필요한 부하를 차단한다.

### 2단계: DB 계층 최적화 (architecture-db 위임)

DB 쿼리 최적화와 인덱싱은 architecture-db 스킬의 영역이다. 핵심 원칙만 요약하면 다음과 같다.

**최적화 순서를 반드시 지킨다:**

```
1. 슬로우 쿼리 최적화    <- 가장 먼저 (비용 최소)
2. 인덱스 적용           <- 읽기 up, 쓰기 down 트레이드오프
3. 애플리케이션 캐시 활용  <- DB 부하 감소
4. 역정규화              <- 최후의 보루
```

**EXPLAIN ANALYZE로 실행 계획을 확인한다.** 대형 테이블에서 Seq Scan이 나타나면 경고 신호다. Index Scan 또는 Index-Only Scan으로 전환해야 한다.

**인덱스 설계는 테이블 구조가 아니라 쿼리 워크로드를 따른다:**

- 복합 인덱스: 등호(=) 조건 컬럼을 범위 조건 컬럼보다 앞에 배치
- 커버링 인덱스: 쿼리에 필요한 모든 컬럼을 인덱스에 포함하여 테이블 룩업 제거
- 부분 인덱스: WHERE 절로 행의 부분 집합만 인덱싱하여 저장 공간과 유지 비용 절감

```sql
-- 좋음: 등호 컬럼 먼저, 커버링 인덱스 활용
CREATE INDEX idx_status_created ON orders (status, created_at);
CREATE INDEX idx_covering ON users (status) INCLUDE (email);

-- 나쁨: 범위 컬럼이 먼저 -> status 필터에 인덱스 활용 불가
CREATE INDEX idx_created_status ON orders (created_at, status);
```

**N+1 문제를 감지하고 제거한다.** 1개 쿼리로 N개 부모를 가져온 후 N개 추가 쿼리로 자식을 개별 조회하는 패턴은 JOIN 또는 IN 절로 1-2개 쿼리로 병합한다.

### 3단계: API-DB 연결점

API 설계 결정이 DB 성능에 직접 영향을 미치는 핵심 연결점을 정리한다.

| API 설계 결정 | DB 영향 | 권장 |
|--------------|---------|------|
| 페이지네이션 방식 | Offset은 대규모에서 full scan 유발 | Cursor/Keyset + 인덱싱된 불변 필드 사용 |
| 응답 필드 선택 | SELECT * 는 커버링 인덱스 무력화 | 필요한 컬럼만 SELECT |
| 필터/정렬 파라미터 | 쿼리 파라미터가 곧 WHERE/ORDER BY | 자주 쓰이는 필터 조합에 복합 인덱스 설계 |
| 목록 엔드포인트 기본 정렬 | 인덱스 없는 ORDER BY는 filesort 유발 | 기본 정렬 키를 인덱스와 일치시킴 |

---
> **관련 스킬 참조:**
> - DB 스키마 설계, 인덱스 전략, EXPLAIN ANALYZE 쿼리 최적화 -> **architecture-db** 스킬
> - Django ORM에서 select_related/prefetch_related로 N+1 해결 -> **implementation-django** 스킬
> - Django Ninja에서 API 엔드포인트 구현, Schema 정의, 스로틀링 -> **implementation-django-ninja** 스킬

## Validation

| 항목 | 결과 |
|------|------|
| Primary 스킬 응답 구조 준수 | OK - [주요 내용] + [관련 스킬 참조] 구조 |
| 설계 모드 적용 | OK - API-DB 연결 관점에서 설계 가이드 제시 |
| 참조 로딩 규칙 준수 | OK - pagination.md, rest-principles.md, rate-limit-idempotency.md, index-and-performance.md, query-optimization.md 참조 |
| 위임 경계 명확 | OK - DB 최적화 상세는 architecture-db로 위임 명시 |
| 관련 스킬 참조 템플릿 | OK - 정확한 템플릿 형식 사용 |
| 크로스 스킬 연결 자연스러움 | OK - API 페이지네이션 -> DB 인덱싱, 응답 필드 -> 커버링 인덱스, 필터 파라미터 -> 복합 인덱스 등 실질적 연결 |
