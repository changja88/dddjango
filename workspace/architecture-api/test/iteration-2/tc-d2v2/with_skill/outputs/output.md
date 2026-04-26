# API 버전 전략 설계

현재 상황 요약: 퍼블릭 API v1이 2년째 운영 중이며 외부 파트너 50개사가 연동 중이다. 다음 달에 사용자 모델 구조 변경과 결제 API 재설계라는 Breaking Change가 예정되어 있고, 일부 레거시 엔드포인트의 제거도 필요하다.

---

## 1. 버전 관리 전략

### 채택 전략: URL Path (메이저) + Header (마이너 조정)

50개 외부 파트너가 연동하는 퍼블릭 API이므로, 버전이 즉시 보이고 라우팅이 명확한 URL Path 방식을 메이저 버전 단위로 사용한다. 마이너 변경(필드 추가, 선택적 파라미터 등)은 Non-Breaking이므로 버전을 올리지 않고 동일 메이저 버전 내에서 처리한다.

```
메이저 버전: URL Path
  /api/v1/users
  /api/v2/users

마이너 조정: 커스텀 헤더 (선택적)
  X-API-Version: 2026-04-15
```

### 새 버전(v2)을 만드는 기준

다음 중 하나라도 해당하면 새 메이저 버전을 도입한다:

| 변경 유형 | Breaking 여부 | 새 버전 필요 |
|----------|:----------:|:----------:|
| 응답에 필드 추가 | X | X |
| 선택적 요청 파라미터 추가 | X | X |
| 필드 제거 | **O** | **O** |
| 필드 이름 변경 | **O** | **O** |
| 필드 타입 변경 | **O** | **O** |
| 필수 파라미터 추가 | **O** | **O** |
| URL 경로 변경 | **O** | **O** |
| 상태 코드 변경 | **O** | **O** |
| 에러 형식 변경 | **O** | **O** |

이번 경우, 사용자 모델 구조 변경(필드 이름/타입 변경)과 결제 API 재설계(URL 경로 및 요청/응답 구조 변경)가 모두 Breaking Change에 해당하므로 v2 도입이 필수다.

### v2 스코프 결정

v2에 포함할 변경과 포함하지 않을 변경을 명확히 분리한다:

```
v2에 포함 (Breaking Change):
  - 사용자 모델: name → first_name + last_name (필드 분리)
  - 사용자 모델: id 타입 변경 (int → UUID string) 등 구조적 변경
  - 결제 API: /v1/payments → /v2/payments (요청/응답 재설계)
  - 레거시 엔드포인트 정리

v2에 포함하지 않음 (Non-Breaking, v1에서 바로 적용):
  - 응답 필드 추가 (새 메타데이터 등)
  - 선택적 파라미터 추가
  - 새 엔드포인트 추가
```

---

## 2. v1 -> v2 마이그레이션 계획

### 2.1 검증: Shadow Traffic (Dark Reading)

v2를 프로덕션에 배포하기 전에, 실제 v1 트래픽의 복사본을 v2에 보내서 응답을 비교한다. 프로덕션 응답은 항상 v1이 담당하므로 파트너에게 영향을 주지 않는다.

```
파트너 요청 → v1 API (실제 응답 반환)
           ↘ v2 API (응답 비교만, 폐기)
                ↓
           불일치 로그 → 모니터링 대시보드
```

Shadow Traffic 운영 절차:

```
1단계 (1주차): 내부 트래픽만 Shadow 전송
  - 내부 서비스 간 호출을 v2로 복제
  - 응답 불일치 분석 및 v2 수정

2단계 (2~3주차): 전체 트래픽의 10% Shadow 전송
  - 다양한 파트너 패턴 커버
  - 불일치율 목표: 0.1% 미만

3단계 (4주차): 전체 트래픽 100% Shadow 전송
  - 최종 검증, 성능 측정
  - 불일치율 0.01% 미만 달성 시 v2 공개 준비 완료
```

### 2.2 단계적 롤아웃: 파트너 Tier별 전환

50개 파트너를 Tier로 분류하여 단계적으로 마이그레이션한다.

| Tier | 대상 | 예상 수 | 마이그레이션 시점 | 지원 수준 |
|------|------|--------|----------------|----------|
| Tier 1 | 핵심 파트너 (매출 상위, 트래픽 상위) | 5~8개사 | v2 공개 후 즉시 | 전담 엔지니어 배정, 1:1 기술 지원, 사전 미팅 |
| Tier 2 | 중요 파트너 (정기 트래픽) | 15~20개사 | Tier 1 완료 후 1개월 | 마이그레이션 가이드 + 그룹 Q&A 세션 |
| Tier 3 | 일반 파트너 (소량 트래픽) | 25~30개사 | Tier 2 완료 후 1개월 | 셀프 서비스 문서 + 자동 마이그레이션 도구 |

### 2.3 호환성 어댑터 (Shim) 운영

마이그레이션 기간 동안 v1 요청을 v2 서버에서 처리할 수 있도록 Shim 레이어를 운영한다. 이를 통해 서버는 v2 코드베이스 하나만 유지하면서 v1 클라이언트도 지원한다.

```
v1 클라이언트 → Shim (v1 요청 → v2 형식 변환) → v2 서버
                    ↓
              v2 응답 → v1 형식 변환 → v1 클라이언트
```

Shim 적용 범위:

```
사용자 API Shim:
  - v1 요청의 name 필드 → v2의 first_name + last_name으로 분리
  - v2 응답의 first_name + last_name → v1의 name으로 합침

결제 API Shim:
  - v1 요청 구조 → v2 요청 구조로 매핑
  - v2 응답 구조 → v1 응답 구조로 매핑
```

Shim은 임시 솔루션이다. v1 Sunset 날짜와 동시에 Shim도 제거한다. 영구적으로 유지하면 기술 부채가 된다.

### 2.4 파트너 커뮤니케이션 일정

```
D-60 (v2 공개 2개월 전):
  - 마이그레이션 공지 발송 (이메일 + 개발자 포털)
  - v2 API 문서 초안 공개
  - Tier 1 파트너 사전 미팅

D-30 (v2 공개 1개월 전):
  - v2 Sandbox 환경 오픈
  - 마이그레이션 가이드 공개
  - Tier 1 파트너 v2 Sandbox 테스트 시작

D-Day (v2 공개):
  - v2 프로덕션 오픈
  - v1에 Deprecation 헤더 추가
  - Tier 1 파트너 프로덕션 전환 시작
```

---

## 3. v1 Deprecation 일정과 프로세스

### 3.1 전체 일정 (최소 12개월 유지)

파트너 50개사가 연동하는 퍼블릭 API이므로, 최소 마이그레이션 기간 6개월 권장 기준보다 넉넉한 12개월을 적용한다.

```
2026-05 (M+0): v2 프로덕션 공개
  - v1과 v2 병행 운영 시작
  - v1 응답에 Deprecation 헤더 추가

2026-08 (M+3): Deprecation 경고 강화
  - v1 응답 본문에 _deprecation 객체 추가
  - 마이그레이션 미완료 파트너에 개별 연락

2026-11 (M+6): v1 기능 동결
  - v1에 신규 기능 추가 중단
  - 보안 패치만 적용
  - 미전환 파트너에 2차 경고

2027-02 (M+9): v1 Rate Limit 축소
  - v1의 Rate Limit을 단계적으로 축소 (기존의 50%)
  - 미전환 파트너에 최종 경고

2027-05 (M+12): v1 제거
  - v1 엔드포인트에 410 Gone 반환
  - Shim 레이어 제거
```

### 3.2 단계별 Deprecation 응답

**Phase 1 - 공지 (M+0, v2 공개 시점부터)**

v1의 모든 응답에 Deprecation 헤더를 추가한다:

```http
HTTP/1.1 200 OK
Deprecation: true
Sunset: Thu, 01 May 2027 00:00:00 GMT
Link: <https://api.example.com/docs/migrate-v2>; rel="deprecation"
```

**Phase 2 - 경고 (M+3부터)**

응답 본문에 `_deprecation` 객체를 추가한다:

```json
{
  "data": {
    "id": "user_123",
    "name": "Alice Kim"
  },
  "_deprecation": {
    "message": "v1 API는 2027-05-01에 제거됩니다. v2로 마이그레이션하세요.",
    "migration_guide": "https://api.example.com/docs/migrate-v2",
    "sunset_date": "2027-05-01"
  }
}
```

**Phase 3 - 제거 (M+12)**

v1 엔드포인트 요청 시 410 Gone을 RFC 9457 Problem Details 형식으로 반환한다:

```http
HTTP/1.1 410 Gone
Content-Type: application/problem+json
```

```json
{
  "type": "https://api.example.com/probs/endpoint-removed",
  "title": "This API version has been removed.",
  "status": 410,
  "detail": "v1 API는 2027-05-01에 제거되었습니다. v2를 사용하세요: https://api.example.com/v2/",
  "instance": "/v1/users"
}
```

### 3.3 레거시 엔드포인트 제거

"곧 제거 예정"인 레거시 엔드포인트는 v2에 포함하지 않고, v1에서도 별도의 가속 Deprecation 일정을 적용한다:

```
레거시 엔드포인트 Deprecation (v1 내부):
  M+0: Deprecation 헤더 + 응답 본문 경고
  M+3: 410 Gone 반환 (v2보다 빠른 일정)

이유: 이미 대체 엔드포인트가 존재하며, v2에서는 아예 제공하지 않으므로
     더 짧은 마이그레이션 기간(3개월)을 적용한다.
```

---

## 4. 하위 호환성 유지 규칙

### 4.1 Non-Breaking Change (버전 변경 없이 허용)

동일 메이저 버전 내에서 자유롭게 적용 가능한 변경:

```
허용:
  - 응답에 새 필드 추가
  - 선택적 요청 파라미터 추가
  - 새 엔드포인트 추가
  - 새 HTTP 메서드 지원 추가
  - 에러 메시지 텍스트 변경 (구조는 유지)
  - 더 넓은 범위의 값 허용 (예: 문자열 길이 제한 완화)
```

### 4.2 절대 금지 (Breaking Change, 새 버전 필수)

동일 메이저 버전 내에서 절대 해서는 안 되는 변경:

```
금지:
  - 기존 필드 제거
  - 필드 이름 변경
  - 필드 타입 변경
  - 필수 파라미터 추가
  - URL 경로 변경
  - HTTP 상태 코드 의미 변경
  - 에러 응답 구조 변경
  - 인증 방식 변경
  - 기본 페이지네이션 크기 변경
```

### 4.3 클라이언트 견고성 원칙 (Robustness Principle)

파트너에게 다음 원칙을 가이드한다:

```
"보내는 것은 엄격하게, 받는 것은 관대하게" (Postel's Law)

- 클라이언트는 인식하지 못하는 필드를 무시해야 한다
- 서버가 새 필드를 추가해도 클라이언트는 깨지지 않아야 한다
- 열거형(enum) 값이 추가될 수 있으므로 unknown 처리를 구현해야 한다
```

이 원칙을 API 문서에 명시하고, 파트너 온보딩 가이드에 포함한다. 이를 준수하는 클라이언트는 Non-Breaking Change에 의한 장애를 방지할 수 있다.

### 4.4 API 변경 이력 관리

모든 API 변경은 Changelog에 기록하고 파트너에게 통보한다:

```
CHANGELOG 형식:

## 2026-05-01
### Added (Non-Breaking)
- GET /v2/users 응답에 created_at 필드 추가
- POST /v2/users에 선택적 파라미터 timezone 추가

### Deprecated
- GET /v1/users — 2027-05-01 제거 예정

### Removed
- GET /v1/legacy-endpoint — 제거됨, 대체: GET /v1/new-endpoint
```

---

## 5. 필드 변경 시 구체적 마이그레이션 패턴

### 5.1 Expand-and-Contract 패턴 (필드 이름 변경)

DB 마이그레이션과 동일한 원칙을 API 응답 필드에 적용한다. 한 번에 필드를 제거하거나 이름을 바꾸는 것은 절대 하지 않는다.

**예시: 사용자 모델의 `name` -> `first_name` + `last_name`**

```
Phase 1 — Expand (Non-Breaking, v1에서 바로 적용)
--------------------------------------------------
v1 응답에 새 필드를 기존 필드와 함께 추가한다.
버전을 올리지 않아도 안전하다 (필드 추가는 Non-Breaking).

GET /api/v1/users/123
{
  "id": "user_123",
  "name": "Alice Kim",          ← 기존 (유지)
  "first_name": "Alice",        ← 신규 추가
  "last_name": "Kim",           ← 신규 추가
  "email": "alice@example.com"
}

요청도 양쪽 모두 허용:
POST /api/v1/users
  name만 보내도 됨 (서버에서 분리)
  first_name + last_name만 보내도 됨 (서버에서 name 생성)
```

```
Phase 2 — Migrate (Deprecation 표시, 파트너 안내)
--------------------------------------------------
v1 응답에 Deprecation 신호를 추가하고, 파트너에게 새 필드 사용을 안내한다.

응답 헤더:
  Deprecation: true
  Sunset: Thu, 01 May 2027 00:00:00 GMT
  Link: <https://api.example.com/docs/migration/name-split>; rel="deprecation"

이 기간 동안:
  - name 필드 사용량 모니터링 (API Analytics)
  - 아직 name을 사용하는 파트너에 개별 연락
  - 마이그레이션 가이드 제공
```

```
Phase 3 — Contract (Breaking, v2에서 기존 필드 제거)
--------------------------------------------------
마이그레이션 기간 종료 후, v2에서는 name 필드를 제공하지 않는다.

GET /api/v2/users/123
{
  "id": "user_123",
  "first_name": "Alice",
  "last_name": "Kim",
  "email": "alice@example.com"
}

v1에서 name을 요청하면:
  - Shim이 first_name + last_name을 합쳐서 name으로 반환 (마이그레이션 기간 중)
  - v1 Sunset 이후에는 410 Gone 반환
```

### 5.2 필드 타입 변경 패턴

**예시: 사용자 ID `int` -> `UUID string`**

타입 변경은 기존 필드 이름을 그대로 바꿀 수 없다. 새 필드를 추가하는 방식으로 처리한다.

```
Phase 1 — Expand (v1에서 양쪽 필드 제공):

GET /api/v1/users/123
{
  "id": 123,                              ← 기존 (int, 유지)
  "uuid": "550e8400-e29b-41d4-a716-446655440000",  ← 신규 (string)
  "name": "Alice Kim"
}

Phase 2 — Migrate (파트너에게 uuid 사용 안내):
  - uuid를 primary identifier로 전환하도록 안내
  - 모든 엔드포인트에서 uuid로도 조회 가능하게 지원
    GET /api/v1/users/123          (기존 int ID)
    GET /api/v1/users/550e8400...  (새 UUID)

Phase 3 — Contract (v2에서 id를 UUID string으로 통일):

GET /api/v2/users/550e8400-e29b-41d4-a716-446655440000
{
  "id": "550e8400-e29b-41d4-a716-446655440000",  ← UUID string
  "first_name": "Alice",
  "last_name": "Kim"
}
```

### 5.3 결제 API 재설계 패턴

URL 경로와 요청/응답 구조가 동시에 바뀌는 대규모 변경은 Expand-and-Contract를 엔드포인트 단위로 적용한다.

```
Phase 1 — Expand (v1에 새 엔드포인트 추가, 기존 유지):

기존: POST /api/v1/payments (유지)
신규: POST /api/v1/payment-intents (추가, v2 구조 미리 노출)

이렇게 하면 파트너가 v2 전환 전에 새 구조를 v1 환경에서 테스트할 수 있다.

Phase 2 — Migrate (기존 엔드포인트 Deprecation):

POST /api/v1/payments 응답에:
  Deprecation: true
  _deprecation: { "use_instead": "/api/v1/payment-intents" }

Phase 3 — Contract (v2에서 정리):

v2에는 payment-intents만 존재:
  POST /api/v2/payment-intents

v1의 payments와 payment-intents 모두 Sunset 일정에 따라 제거.
```

### 5.4 Shim 변환 규칙 명세

마이그레이션 기간 동안 Shim이 처리하는 변환 규칙을 명확히 정의한다:

```
사용자 API Shim 변환 규칙:
--------------------------------------------------
요청 변환 (v1 → v2):
  v1 { name: "Alice Kim" }
  → v2 { first_name: "Alice", last_name: "Kim" }
  (공백 기준 첫 단어: first_name, 나머지: last_name)

  v1 { id: 123 }
  → v2 { id: "550e8400-..." }  (매핑 테이블 참조)

응답 변환 (v2 → v1):
  v2 { first_name: "Alice", last_name: "Kim" }
  → v1 { name: "Alice Kim", first_name: "Alice", last_name: "Kim" }

  v2 { id: "550e8400-..." }
  → v1 { id: 123, uuid: "550e8400-..." }  (매핑 테이블 참조)

결제 API Shim 변환 규칙:
--------------------------------------------------
요청 변환 (v1 → v2):
  v1 POST /payments { amount, currency, source }
  → v2 POST /payment-intents { amount, currency, payment_method }

응답 변환 (v2 → v1):
  v2 { payment_intent: {...} }
  → v1 { payment: {...} }  (필드 매핑 적용)
```

---

## 종합 타임라인

```
2026-04 (현재)
  ├── 파트너 Tier 분류 완료
  ├── v2 설계 확정 및 문서화
  └── Shadow Traffic 인프라 구축

2026-04 ~ 2026-05 (v2 공개 전)
  ├── v1에 Expand 적용 (새 필드 추가, Non-Breaking)
  ├── Shadow Traffic 검증 (4주간)
  ├── v2 Sandbox 환경 오픈
  └── Tier 1 파트너 사전 미팅 및 Sandbox 테스트

2026-05 (M+0): v2 프로덕션 공개
  ├── v1 Deprecation 헤더 추가 (Phase 1)
  ├── Shim 레이어 가동
  └── Tier 1 파트너 v2 전환 시작

2026-06 (M+1): Tier 1 전환 완료
  └── Tier 2 파트너 전환 시작

2026-07 (M+2): Tier 2 전환 완료
  └── Tier 3 파트너 전환 시작

2026-08 (M+3)
  ├── v1 응답 본문에 _deprecation 경고 추가 (Phase 2)
  ├── 레거시 엔드포인트 410 Gone 반환 (가속 Deprecation)
  └── Tier 3 파트너 전환 완료 목표

2026-11 (M+6): v1 기능 동결
  └── v1 보안 패치만 적용

2027-02 (M+9): v1 Rate Limit 축소
  └── 미전환 파트너 최종 경고

2027-05 (M+12): v1 제거
  ├── v1 전체 엔드포인트 410 Gone (Phase 3)
  ├── Shim 레이어 제거
  └── v1 서버 인프라 해제
```
