# API 변경 계획 리뷰 — 하위 호환성 분석

## 요약

제안된 5개 변경 사항 중 **4개가 Breaking Change**이며, 같은 v1에 공지 없이 적용할 경우 기존 클라이언트가 즉시 장애를 일으킬 수 있다. 유일하게 안전한 변경은 `created_at` 필드 추가 1건뿐이다.

---

## 변경 사항별 분석

### 1. `name` 필드를 `first_name`, `last_name`으로 분리 -- Breaking

```
[Versioning — 필드 이름 변경 / 필드 제거]
기존 name 필드가 사라지고 first_name, last_name이 추가되므로 "필드 제거"와 "필드 이름 변경"에 모두 해당한다.
기존 클라이언트는 response.name을 참조하고 있으며, 이 필드가 사라지면 즉시 오류가 발생한다.
```

**판정**: Breaking Change (필드 제거 + 필드 이름 변경)

### 2. `age` 필드 제거 -- Breaking

```
[Versioning — 필드 제거]
응답에서 기존 필드를 제거하는 것은 명시적인 Breaking Change이다.
기존 클라이언트가 age 필드를 사용하고 있다면 (UI 표시, 로직 분기 등) 해당 기능이 깨진다.
```

**판정**: Breaking Change (필드 제거)

### 3. `phone` 필드 추가 (필수) -- Breaking

```
[Versioning — 필수 파라미터 추가]
응답에 선택적 필드를 추가하는 것은 Non-Breaking이지만, "필수(required)"라는 표현이
요청 측에도 적용된다면(예: 사용자 생성/수정 시 phone이 필수) 이는 Breaking Change이다.
기존 클라이언트는 phone 없이 POST/PUT 요청을 보내고 있으므로, 해당 요청이
422 Validation Error로 실패하게 된다.
```

**판정**: 응답에 추가만 하는 것이면 Non-Breaking이지만, 요청에서 필수(required)로 강제하면 Breaking Change (필수 파라미터 추가)

### 4. `id` 타입을 integer에서 UUID string으로 변경 -- Breaking

```
[Versioning — 필드 타입 변경]
id 필드의 타입을 변경하는 것은 가장 심각한 Breaking Change 중 하나이다.
- 기존 클라이언트가 id를 정수형으로 파싱/저장하고 있다면 전부 실패한다
- URL 경로도 영향 받는다: GET /api/v1/users/123 vs GET /api/v1/users/550e8400-e29b-41d4-a716-446655440000
- 외부 시스템에 저장된 기존 id 참조가 모두 깨진다
- 데이터베이스 마이그레이션도 동반되어야 한다
```

**판정**: Breaking Change (필드 타입 변경) -- 가장 높은 위험도

### 5. 응답에 `created_at` 필드 추가 -- Non-Breaking

```
[Versioning — 필드 추가 (응답)]
응답에 새로운 선택적 필드를 추가하는 것은 Non-Breaking Change이다.
Robustness Principle에 따라 클라이언트는 인식하지 못하는 필드를 무시하도록 설계되어야 하므로,
이 변경은 기존 클라이언트에 영향을 주지 않는다.
```

**판정**: Non-Breaking -- 유일하게 안전한 변경

---

## "별도 공지 없이 다음 배포에 바로 적용" 문제

이 배포 계획은 Deprecation 프로세스를 완전히 무시하고 있다. 버전 관리 원칙에 따르면:

1. **Deprecation 공지**가 선행되어야 한다 (API 문서에 명시, 변경 이력에 기록)
2. **Sunset 헤더**를 응답에 포함하여 만료 날짜를 알려야 한다
3. **최소 6개월~1년의 마이그레이션 기간**을 제공해야 한다
4. **대체 API 안내** 및 마이그레이션 가이드를 제공해야 한다

공지 없이 배포하면 기존 클라이언트가 아무런 준비 없이 장애를 겪게 된다.

---

## 권장 조치

### 같은 v1에서 안전하게 적용 가능한 변경 (즉시 배포 가능)

| 변경 | 방법 |
|------|------|
| `created_at` 추가 | 그대로 적용 (Non-Breaking) |
| `phone` 추가 | **선택적(optional)** 필드로 추가하면 Non-Breaking |

### 새 버전(v2)으로 이동해야 하는 변경

| 변경 | 이유 |
|------|------|
| `name` -> `first_name`, `last_name` 분리 | 필드 제거/이름 변경 |
| `age` 제거 | 필드 제거 |
| `id` 타입 변경 (int -> UUID) | 필드 타입 변경 |

### 구체적 실행 방안

**1단계 -- v1에서 점진적 전환 준비**
```
GET /api/v1/users/123
응답: {
  "id": 123,
  "name": "Alice",              // 유지 (deprecated 표시)
  "first_name": "Alice",        // 신규 추가 (Non-Breaking)
  "last_name": "",              // 신규 추가 (Non-Breaking)
  "email": "alice@test.com",
  "age": 30,                    // 유지 (deprecated 표시)
  "phone": "+821012345678",     // 선택적으로 추가 (Non-Breaking)
  "created_at": "2024-01-15T09:00:00Z"  // 추가 (Non-Breaking)
}
```
- Sunset 헤더 추가: `Sunset: <6개월 후 날짜>`
- API 문서에 deprecated 필드 명시

**2단계 -- v2 엔드포인트 신설**
```
GET /api/v2/users/550e8400-e29b-41d4-a716-446655440000
응답: {
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "first_name": "Alice",
  "last_name": "",
  "email": "alice@test.com",
  "phone": "+821012345678",
  "created_at": "2024-01-15T09:00:00Z"
}
```

**3단계 -- 마이그레이션 기간 (최소 6개월) 후 v1 제거**

---

## 리뷰 체크리스트

- [N/A] Verbs in URL paths -- 해당 없음, URL 구조 변경 없음
- [N/A] Wrong HTTP method -- 해당 없음, GET 유지
- [N/A] Inconsistent or wrong status codes -- 해당 없음
- [N/A] Missing or non-standard error response format -- 해당 없음
- [N/A] Singular nouns for collection resources -- 해당 없음
- [N/A] Missing pagination for list endpoints -- 해당 없음 (단일 리소스 조회)
- [N/A] No versioning strategy -- v1 URL path 전략 사용 중
- [FAIL] Breaking changes without version bump -- **4개 Breaking Change를 같은 v1에 적용하려 하고 있음**
- [N/A] Sensitive data in query parameters -- 해당 없음
- [N/A] Missing idempotency handling -- 해당 없음 (GET 요청)
