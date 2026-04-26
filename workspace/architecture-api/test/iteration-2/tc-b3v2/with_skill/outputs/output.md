# API 변경 계획 리뷰

## 요약

제시된 5개 변경 중 **4개가 Breaking Change**이며, 이를 같은 v1에 공지 없이 적용하면 외부 파트너 20개사의 클라이언트가 즉시 장애를 겪는다. 아래에서 각 변경의 문제점과 올바른 접근법을 제시한다.

---

## 변경별 분석

### 1. `name` 필드를 `first_name`, `last_name`으로 분리

[Breaking Change: 필드 제거 + 필드 이름 변경] — 기존 `name` 필드를 제거하고 새 필드로 대체하면 `response.name`을 참조하는 모든 클라이언트 코드가 즉시 깨진다.

**올바른 접근: Expand-and-Contract 패턴 적용**

```
Phase 1 (Expand) — v1에서 바로 적용 가능, Non-Breaking:
{
  "id": 123,
  "name": "Alice Kim",           <- 기존 (유지)
  "first_name": "Alice",         <- 신규 추가
  "last_name": "Kim",            <- 신규 추가
  "email": "alice@test.com",
  "age": 30
}

Phase 2 (Migrate) — Deprecation 헤더 추가, 6개월 유지:
Deprecation: true
Sunset: Sat, 01 Oct 2026 00:00:00 GMT
Link: <https://api.example.com/docs/migration/name-split>; rel="deprecation"

Phase 3 (Contract) — 6개월 후 name 제거, v2 도입:
{
  "id": 123,
  "first_name": "Alice",
  "last_name": "Kim",
  "email": "alice@test.com"
}
```

Phase 1은 필드 추가이므로 Non-Breaking이다. 버전을 올리지 않고 v1에서 안전하게 적용할 수 있다. Phase 3에서 `name`을 제거할 때 비로소 Breaking이 되며, 이때 v2를 도입한다.

---

### 2. `age` 필드 제거

[Breaking Change: 필드 제거] — 응답에서 기존 필드를 제거하는 것은 Breaking Change이다. `response.age`를 참조하는 클라이언트가 `undefined`/`null`을 받게 되어 예기치 않은 동작을 일으킨다.

**올바른 접근:**

- **즉시 제거는 금지.** Deprecation 프로세스를 따른다.
- Phase 1: `age` 필드에 Deprecation 표시 (헤더 + 문서). 필드는 계속 반환한다.
- Phase 2: 응답 본문에 `_deprecation` 경고를 추가하여 클라이언트에게 명시적으로 알린다.
- Phase 3: 최소 6개월 후, v2에서 `age` 필드를 제거한다.

```
Phase 2 응답 예시:
{
  "id": 123,
  "name": "Alice Kim",
  "email": "alice@test.com",
  "age": 30,
  "_deprecation": {
    "message": "age 필드는 2026-10-01에 제거됩니다",
    "migration_guide": "https://api.example.com/docs/migration/remove-age",
    "sunset_date": "2026-10-01"
  }
}
```

---

### 3. `phone` 필드 추가 (필수)

[Breaking Change: 필수 파라미터 추가] — 응답에 필드를 추가하는 것 자체는 Non-Breaking이지만, "필수"라는 표현이 **요청 시 필수 입력**을 의미한다면 Breaking Change이다. 기존 클라이언트는 `phone`을 보내지 않으므로 요청이 실패하게 된다.

**올바른 접근:**

- **응답에 `phone` 추가**: Non-Breaking. v1에서 바로 적용 가능.
- **요청에서 `phone`을 필수로 요구**: Breaking. 새 버전(v2)에서만 적용해야 한다.
- v1에서는 `phone`을 **선택적(optional) 파라미터**로 추가하고, v2에서 필수로 전환하는 것이 안전한 경로이다.

---

### 4. `id` 타입을 integer에서 UUID string으로 변경

[Breaking Change: 필드 타입 변경] — 이것은 가장 파괴적인 변경이다. `id`는 리소스 식별자이므로 모든 클라이언트의 모든 API 호출에 영향을 준다. integer로 파싱하던 코드, URL 구성 로직, DB 외래키 참조 등이 전부 깨진다.

**올바른 접근:**

- 이 변경은 **반드시 v2에서 도입**해야 한다.
- v1과 v2를 병행 운영하면서 마이그레이션 기간을 제공한다.
- **Expand-and-Contract** 적용이 가능하다면, 과도기에 양쪽 모두 제공:

```
과도기 v1 응답:
{
  "id": 123,                         <- 기존 (유지)
  "uuid": "550e8400-e29b-41d4-a716-446655440000",  <- 신규 추가
  ...
}

v2 응답:
{
  "id": "550e8400-e29b-41d4-a716-446655440000",    <- UUID로 변경
  ...
}
```

- **Shadow Traffic 검증**: v2 API에 실제 트래픽 복사본을 보내 응답을 비교하고, 불일치를 모니터링 대시보드에서 확인한 후 전환한다.

---

### 5. 응답에 `created_at` 필드 추가

[Non-Breaking: 응답 필드 추가] — 이것은 **유일하게 안전한 변경**이다. 응답에 새 필드를 추가하는 것은 Non-Breaking Change이며, 잘 설계된 클라이언트는 인식하지 못하는 필드를 무시한다 (Robustness Principle).

**즉시 v1에 적용 가능.** 별도의 버전 관리나 마이그레이션이 필요 없다.

---

## 프로세스 문제점

### "별도 공지 없이 다음 배포에 바로 적용"

이것이 가장 큰 문제이다. Deprecation 프로세스를 완전히 무시하고 있다.

- 외부 파트너 20개사가 사용 중인 API에 Breaking Change를 공지 없이 적용하면 **즉시 장애가 발생**한다.
- Deprecation 프로세스는 반드시 5단계를 거쳐야 한다: 공지 -> Sunset 헤더 -> 마이그레이션 기간(최소 6개월) -> 대체 API 안내 -> 제거.
- 20개 파트너의 규모라면 **파트너 Tier별 단계적 롤아웃**을 적용해야 한다:

| Tier | 대상 | 마이그레이션 시점 | 지원 수준 |
|------|------|----------------|----------|
| Tier 1 | 핵심 파트너 (매출 상위) | 최우선, 1:1 기술 지원 | 전담 엔지니어 |
| Tier 2 | 중요 파트너 | 2차, 그룹 세션 | 마이그레이션 가이드 + Q&A |
| Tier 3 | 일반 파트너 | 3차, 셀프 서비스 | 문서 + 자동화 도구 |

---

## 권장 실행 계획

```
즉시 (v1, Non-Breaking):
  - created_at 필드 추가 (변경 #5)
  - first_name, last_name 필드 추가 — name은 유지 (변경 #1 Phase 1)
  - uuid 필드 추가 — id는 유지 (변경 #4 과도기)
  - phone 필드를 선택적(optional)으로 추가 (변경 #3)
  - age 필드에 Deprecation 헤더 추가 (변경 #2 Phase 1)

6개월 후 (v2, Breaking):
  - name 필드 제거
  - age 필드 제거
  - id 타입을 UUID string으로 변경
  - phone 필드를 필수로 전환
  - v1은 Shim(호환성 어댑터)을 통해 유지, Sunset 날짜 설정
  - Shadow Traffic으로 v2 검증 후 단계적 롤아웃

12개월 후:
  - v1 완전 제거 (410 Gone + RFC 9457 Problem Details 응답)
  - Shim 제거
```

### 즉시 적용 후 v1 응답 예시

```json
{
  "id": 123,
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Alice Kim",
  "first_name": "Alice",
  "last_name": "Kim",
  "email": "alice@test.com",
  "age": 30,
  "phone": null,
  "created_at": "2024-01-15T09:30:00Z"
}
```

```
응답 헤더:
Deprecation: true
Sunset: Sat, 01 Oct 2026 00:00:00 GMT
Link: <https://api.example.com/docs/migration/v2>; rel="deprecation"
```

---

## 핵심 원칙 요약

1. **추가는 자유, 제거는 금지** (Additive changes only) — v1에서는 필드를 추가만 한다.
2. **필드 마이그레이션은 반드시 Expand-and-Contract 3단계** — 한 번에 제거/이름변경하지 않는다.
3. **Breaking Change가 필요하면 새 버전을 만든다** — 같은 v1에 Breaking Change를 넣지 않는다.
4. **마이그레이션 기간은 최소 6개월** — 공지 없는 즉시 적용은 금지이다.
5. **대규모 마이그레이션은 Shadow Traffic으로 검증** 후 Tier별 단계적 롤아웃을 실시한다.
