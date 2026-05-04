# 버전 관리 레퍼런스

세 가지 버전 관리 전략, Stripe 날짜 기반 패턴, Breaking vs Non-Breaking 변경 구분, Deprecation 프로세스.

---

## 세 가지 전략

| 전략 | 예시 | 장점 | 단점 |
|------|------|------|------|
| **URL Path** | `/api/v1/products` | 즉시 보임, 라우팅 쉬움 | REST 원칙 위반, URL 오염 |
| **Header** | `Accept-Version: v1` | 깨끗한 URL, REST 부합 | 브라우저에서 안 보임, 디버깅 어려움 |
| **Query Param** | `?version=1` | 중간 지점, 가시적 | 캐싱 복잡, 필터와 혼동 |

---

## Stripe의 날짜 기반 버전 관리

- URL path: 메이저 버전 (`/v1/charges`)
- 헤더: 실제 버전 (`Stripe-Version: 2024-10-01`)
- 신규 계정은 최신 버전에 자동 고정
- 요청별 오버라이드 가능

---

## Breaking vs Non-Breaking Change

| 변경 유형 | Breaking? | 예시 |
|----------|:---------:|------|
| 필드 추가 (응답) | X | 새 필드 `created_at` 추가 |
| 필드 추가 (요청, 선택) | X | 선택적 파라미터 `filter` 추가 |
| 필드 제거 | **O** | 기존 `name` 필드 삭제 |
| 필드 이름 변경 | **O** | `name` -> `full_name` |
| 필드 타입 변경 | **O** | `id: int` -> `id: string` |
| 필수 파라미터 추가 | **O** | 새 필수 필드 `email` 추가 |
| URL 경로 변경 | **O** | `/users` -> `/accounts` |
| 상태 코드 변경 | **O** | 200 -> 201 |
| 에러 형식 변경 | **O** | 에러 응답 구조 변경 |

---

## Deprecation 프로세스

1. **Deprecation 공지**: API 문서에 명시, 변경 이력에 기록
2. **Sunset 헤더**: 응답에 만료 날짜 포함
   ```
   Sunset: Sat, 01 Mar 2025 00:00:00 GMT
   Deprecation: true
   ```
3. **마이그레이션 기간**: 최소 6개월~1년 유지
4. **대체 API 안내**: 새 엔드포인트 또는 버전으로의 마이그레이션 가이드 제공
5. **제거**: 마이그레이션 기간 종료 후 제거

---

## API 필드 마이그레이션: Expand-and-Contract 패턴

DB 마이그레이션과 동일한 원칙을 API 응답 필드에 적용한다. 필드를 제거하거나 이름을 바꾸는 것은 한 단계에서 절대 하지 않는다.

### 3단계 프로세스

```
1. Expand   : 새 필드를 기존 필드와 함께 추가 (양쪽 모두 반환)
2. Migrate  : 클라이언트에게 새 필드 사용을 안내, 기존 필드에 Deprecation 표시
3. Contract : 마이그레이션 기간 종료 후 기존 필드 제거
```

### 예시: name → first_name + last_name

```
Phase 1 (Expand) — v1에서 바로 적용 가능, Non-Breaking:
{
  "name": "Alice Kim",           ← 기존 (유지)
  "first_name": "Alice",         ← 신규
  "last_name": "Kim"             ← 신규
}

Phase 2 (Migrate) — Deprecation 헤더 추가:
Deprecation: true
Sunset: Sat, 01 Sep 2025 00:00:00 GMT
Link: <https://api.example.com/docs/migration/name-split>; rel="deprecation"

Phase 3 (Contract) — 6개월 후 name 제거:
{
  "first_name": "Alice",
  "last_name": "Kim"
}
```

**핵심**: Phase 1은 필드 추가이므로 Non-Breaking. 버전을 올리지 않고도 안전하게 적용 가능. Phase 3만이 Breaking이며 이때 새 버전(v2)을 도입한다.

---

## 운영 수준 마이그레이션 전술

### Shadow Traffic (Dark Reading)

새 버전의 API에 실제 트래픽의 복사본을 보내서 응답을 비교한다. 프로덕션에는 영향을 주지 않으면서 새 버전의 정확성을 검증할 수 있다.

```
클라이언트 → v1 API (실제 응답 반환)
         ↘ v2 API (응답 비교만, 폐기)
              ↓
         불일치 로그 → 모니터링 대시보드
```

**Stripe의 Scientist 패턴**: 동일 요청을 양쪽 버전에 실행하고, 결과가 다르면 알림. 프로덕션 응답은 항상 v1이 담당.

### 파트너 Tier별 단계적 롤아웃

| Tier | 대상 | 마이그레이션 시점 | 지원 수준 |
|------|------|----------------|----------|
| Tier 1 | 핵심 파트너 (매출 상위) | 최우선, 1:1 기술 지원 | 전담 엔지니어 |
| Tier 2 | 중요 파트너 | 2차, 그룹 세션 | 마이그레이션 가이드 + Q&A |
| Tier 3 | 일반 파트너 | 3차, 셀프 서비스 | 문서 + 자동화 도구 |

### 호환성 어댑터 (Shim) 패턴

v1 클라이언트가 v2 서버와 통신할 수 있도록 중간에 변환 레이어를 둔다.

```
v1 클라이언트 → Shim (v1 요청 → v2 변환) → v2 서버
                    ↓
              v2 응답 → v1 형식 변환 → v1 클라이언트
```

**주의**: Shim은 마이그레이션 기간의 **임시 솔루션**이다. 영구적으로 유지하면 기술 부채가 된다. Sunset 날짜와 함께 Shim 제거 일정도 정한다.

### Deprecation 응답 강화

Sunset 헤더만으로 클라이언트가 인지하지 못할 수 있다. 단계별로 경고를 강화한다:

```
Phase 1 (공지): Deprecation 헤더만
  Deprecation: true
  Sunset: Sat, 01 Mar 2025 00:00:00 GMT
  Link: <https://api.example.com/docs/migrate-v2>; rel="deprecation"

Phase 2 (경고): 응답 본문에 warning 추가
  {
    "data": {...},
    "_deprecation": {
      "message": "이 엔드포인트는 2025-03-01에 제거됩니다",
      "migration_guide": "https://api.example.com/docs/migrate-v2",
      "sunset_date": "2025-03-01"
    }
  }

Phase 3 (제거): 410 Gone + RFC 9457
  HTTP/1.1 410 Gone
  Content-Type: application/problem+json
  {
    "type": "https://api.example.com/probs/endpoint-removed",
    "title": "This endpoint has been removed.",
    "status": 410,
    "detail": "POST /v1/orders was removed on 2025-03-01. Use POST /v2/orders instead.",
    "instance": "/v1/orders"
  }
```

> 출처: Stripe Blog - API Versioning, Prisma - Expand and Contract Pattern

---

## 실전 원칙

- 하나의 전략을 선택하고 **일관되게** 적용
- 일반 패턴: URL path로 메이저 버전, 헤더로 마이너 조정
- 버전 관리 방식을 문서화하고 마이그레이션 경로 제공
- **추가는 자유, 제거는 금지** (Additive changes only)
- Breaking change가 필요하면 새 버전을 만든다
- 클라이언트가 인식하지 못하는 필드를 무시하도록 설계 (Robustness Principle: "보내는 것은 엄격하게, 받는 것은 관대하게")
- 필드 마이그레이션은 반드시 **Expand-and-Contract** 3단계로
- 대규모 마이그레이션은 **Shadow Traffic으로 검증** 후 단계적 롤아웃
