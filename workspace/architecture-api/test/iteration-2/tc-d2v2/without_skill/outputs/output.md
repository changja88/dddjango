# API 버전 전략 설계

## 1. 버전 관리 전략

### 1.1 버전 식별 방식: URL Path Versioning

```
https://api.example.com/v1/users
https://api.example.com/v2/users
```

**선택 근거:**
- 외부 파트너 50개사가 연동 중이므로 버전이 명시적으로 드러나야 한다
- Header 기반 버전(Accept 헤더)은 디버깅과 파트너 커뮤니케이션에서 마찰이 크다
- URL Path 방식은 문서화, 로깅, 모니터링에서 즉시 버전을 식별할 수 있다
- 이미 v1이 URL Path 방식으로 2년간 운영되었으므로 일관성을 유지한다

### 1.2 버전 범위 규칙

| 구분 | 설명 | 예시 |
|------|------|------|
| Major 버전 (v1, v2) | 하위 호환성이 깨지는 변경 | 모델 구조 변경, 필드 삭제, 응답 포맷 변경 |
| Minor 변경 | 기존 버전 내에서 추가 | 새 필드 추가, 새 엔드포인트 추가 |
| Patch 변경 | 기존 버전 내에서 수정 | 버그 수정, 성능 개선 |

**Major 버전을 올려야 하는 경우:**
- 기존 필드의 타입 변경
- 기존 필드 삭제 또는 이름 변경
- 응답 구조(envelope) 변경
- 인증 방식 변경
- 에러 응답 포맷 변경

**Major 버전을 올리지 않는 경우:**
- 새로운 선택적(optional) 필드 추가
- 새로운 엔드포인트 추가
- 새로운 쿼리 파라미터 추가 (기본값이 기존 동작 유지)

### 1.3 동시 운영 정책

```
최대 2개의 Major 버전만 동시 운영한다.
v3 출시 시점에 v1은 반드시 종료되어야 한다.
```

### 1.4 라우팅 아키텍처

```
                    ┌─────────────┐
  Client ──────────>│  API Gateway │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │ Version     │
                    │ Router      │
                    └──┬──────┬───┘
                       │      │
                 ┌─────┴─┐ ┌─┴─────┐
                 │ v1    │ │ v2    │
                 │Handler│ │Handler│
                 └───┬───┘ └───┬───┘
                     │         │
                 ┌───┴─────────┴───┐
                 │  Shared Service  │
                 │  Layer           │
                 └─────────────────┘
```

- API Gateway에서 버전별 라우팅 처리
- 각 버전의 Handler(Controller)는 독립적으로 유지
- 비즈니스 로직(Service Layer)은 공유하되, 버전별 변환 계층(Adapter)을 둔다

---

## 2. v1에서 v2 마이그레이션 계획

### 2.1 전체 타임라인

```
T-8주: v2 내부 설계 완료 및 사내 리뷰
T-6주: v2 Beta 배포 (샌드박스 환경)
T-4주: 얼리 어답터 파트너 5개사 Beta 테스트
T-2주: v2 GA (General Availability) 릴리스
T+0:   v2 공식 출시, v1 Deprecation 공지
T+12주: v1 Sunset Warning 단계 진입
T+24주: v1 최종 종료 (Sunset)
```

### 2.2 검증 단계

#### Phase 1: 내부 검증 (T-8주 ~ T-6주)

```
1. Contract Testing
   - v1 기존 요청/응답 계약을 자동화 테스트로 확보
   - v2 엔드포인트에 대해 동일 시나리오 검증
   - OpenAPI Spec diff 도구로 변경 사항 자동 탐지

2. Shadow Traffic Testing
   - 프로덕션 v1 트래픽을 복제하여 v2로 전송
   - v1 응답과 v2 응답을 비교 (의도된 차이 제외)
   - 성능 지표 비교 (지연시간, 에러율)

3. 데이터 마이그레이션 검증
   - 사용자 모델 구조 변경에 따른 데이터 변환 스크립트 검증
   - 결제 데이터 정합성 확인 (금액 불일치 = 즉시 차단)
```

#### Phase 2: 외부 Beta 검증 (T-4주 ~ T-2주)

```
1. 얼리 어답터 파트너 선정 기준:
   - API 호출량 상위 파트너 2개사
   - 기술적 역량이 높은 파트너 2개사
   - 다양한 사용 패턴을 가진 파트너 1개사

2. Beta 환경 제공:
   - 별도 샌드박스 도메인: https://api-beta.example.com/v2/
   - 프로덕션과 동일한 데이터 구조, 테스트 데이터 제공
   - 전담 기술 지원 채널 (Slack/이메일)

3. 피드백 수집 항목:
   - 마이그레이션 가이드 명확성
   - SDK/라이브러리 호환성
   - 예상치 못한 동작 변경
```

### 2.3 롤아웃 전략

```
단계적 트래픽 전환 (v2 GA 이후):

Week 1-2:  신규 파트너 onboarding은 v2로만 진행
Week 3-4:  얼리 어답터 파트너를 프로덕션 v2로 전환
Week 5-8:  나머지 파트너에게 마이그레이션 지원 시작
Week 9-12: 마이그레이션 완료 목표, 미전환 파트너 집중 지원
```

### 2.4 파트너 관리

```
파트너 분류 (Tier):

Tier 1 (호출량 상위 10개사):
  - 전담 SE(Solutions Engineer) 배정
  - 1:1 마이그레이션 미팅
  - 커스텀 마이그레이션 일정 협의

Tier 2 (중간 규모 20개사):
  - 그룹 웨비나 (2회)
  - 이메일 기반 기술 지원
  - 마이그레이션 체크리스트 제공

Tier 3 (소규모 20개사):
  - 셀프서비스 마이그레이션 가이드
  - FAQ 문서
  - 커뮤니티 포럼 지원
```

**파트너 커뮤니케이션 일정:**

| 시점 | 내용 | 채널 |
|------|------|------|
| T-8주 | v2 변경 사항 사전 안내 | 이메일 + 개발자 포탈 공지 |
| T-4주 | Beta 참여 초대 | 이메일 (얼리 어답터) |
| T+0 | v2 GA 출시 + 마이그레이션 가이드 배포 | 이메일 + 블로그 + 개발자 포탈 |
| T+4주 | 마이그레이션 진행 상황 리마인더 | 이메일 |
| T+8주 | 미전환 파트너 개별 연락 | 이메일 + 전화 |
| T+12주 | v1 Sunset Warning 시작 안내 | 이메일 + API 응답 헤더 |
| T+20주 | 최종 경고 (Sunset 4주 전) | 이메일 + 전화 + API 응답 경고 |
| T+24주 | v1 종료 | 이메일 |

---

## 3. v1 Deprecation 일정과 프로세스

### 3.1 Deprecation 3단계 프로세스

```
┌───────────────┐    ┌────────────────┐    ┌──────────────┐
│  Deprecated   │───>│ Sunset Warning │───>│   Sunset     │
│  (T+0 ~ T+12)│    │ (T+12 ~ T+24) │    │  (T+24)      │
└───────────────┘    └────────────────┘    └──────────────┘
```

### 3.2 Stage 1: Deprecated (T+0 ~ T+12주)

v2 GA 출시와 동시에 v1은 Deprecated 상태로 전환된다.

**API 응답 변경:**

```http
HTTP/1.1 200 OK
Deprecation: true
Sunset: Sat, 26 Sep 2026 00:00:00 GMT
Link: <https://api.example.com/v2/users>; rel="successor-version"
X-API-Warn: "v1 is deprecated. Migrate to v2 by 2026-09-26. See https://docs.example.com/migration"
```

- `Deprecation` 헤더: RFC 8594 표준. 해당 API가 더 이상 권장되지 않음을 표시
- `Sunset` 헤더: RFC 8594 표준. API가 종료되는 정확한 일시
- `Link` 헤더: 후속 버전 URL 안내
- `X-API-Warn`: 사람이 읽을 수 있는 경고 메시지

**이 단계에서 v1은:**
- 정상적으로 동작한다
- 새로운 기능은 추가되지 않는다
- 보안 패치만 적용된다
- 성능 최적화는 하지 않는다

### 3.3 Stage 2: Sunset Warning (T+12주 ~ T+24주)

**API 응답 변경 (추가):**

```http
HTTP/1.1 200 OK
Deprecation: true
Sunset: Sat, 26 Sep 2026 00:00:00 GMT
X-API-Warn: "URGENT: v1 will be shut down on 2026-09-26. Migrate immediately."
```

**추가 조치:**
- v1 Rate Limit을 점진적으로 축소 (기존의 80% -> 60% -> 40%)
- 축소 일정과 수치를 사전에 파트너에게 공지
- v1 API 문서에 "DEPRECATED" 배너 상시 표시
- 미전환 파트너 개별 연락 (Tier 무관)

**Rate Limit 축소 일정:**

| 시점 | v1 Rate Limit | 비고 |
|------|--------------|------|
| T+12주 | 기존의 80% | Sunset Warning 진입 |
| T+16주 | 기존의 60% | 2차 축소 |
| T+20주 | 기존의 40% | 최종 경고 |
| T+24주 | 0% (종료) | Sunset |

### 3.4 Stage 3: Sunset (T+24주)

**v1 종료 처리:**

```http
HTTP/1.1 410 Gone
Content-Type: application/json

{
  "error": {
    "code": "API_VERSION_SUNSET",
    "message": "API v1 has been permanently retired as of 2026-09-26.",
    "migration_guide": "https://docs.example.com/migration/v1-to-v2",
    "successor": "https://api.example.com/v2/"
  }
}
```

- 모든 v1 엔드포인트는 `410 Gone`을 반환한다
- 응답 본문에 마이그레이션 가이드 URL을 포함한다
- 이 상태를 최소 4주간 유지한 후 v1 인프라를 해제한다

### 3.5 레거시 엔드포인트 조기 제거

곧 제거 예정인 레거시 엔드포인트는 v2 출시와 별도로 관리한다.

```
레거시 엔드포인트 제거 절차:

1. 사용량 분석: 지난 90일간 호출한 파트너 식별
2. 개별 통보: 해당 파트너에게 60일 전 사전 통보
3. 대체 안내: 대체 엔드포인트 또는 v2 엔드포인트 안내
4. Deprecation 헤더 추가 (30일간)
5. 410 Gone 반환으로 전환
```

---

## 4. 하위 호환성 유지 규칙

### 4.1 절대 금지 사항 (동일 Major 버전 내)

```
다음 변경은 동일 Major 버전 내에서 절대 수행하지 않는다:

1. 기존 필드 삭제
2. 기존 필드의 타입 변경 (string -> integer 등)
3. 기존 필드의 이름 변경 (user_name -> username)
4. 필수(required) 요청 파라미터 추가
5. 응답 envelope 구조 변경
6. 기존 enum 값 삭제
7. HTTP 메서드 변경 (GET -> POST)
8. URL 경로 변경
9. 인증 방식 변경
10. 에러 코드 체계 변경
```

### 4.2 허용되는 변경 (동일 Major 버전 내)

```
다음 변경은 하위 호환성을 깨지 않으므로 허용한다:

1. 새로운 선택적(optional) 필드를 응답에 추가
2. 새로운 선택적(optional) 요청 파라미터 추가 (기본값 = 기존 동작)
3. 새로운 엔드포인트 추가
4. 기존 enum에 새 값 추가 (클라이언트는 unknown 값 무시 필수)
5. 에러 메시지 텍스트 변경 (코드는 유지)
6. Rate Limit 완화
7. 응답 필드 순서 변경 (JSON은 순서 무관)
```

### 4.3 클라이언트 측 규칙 (파트너 가이드에 명시)

파트너에게 다음 규칙을 SDK 가이드와 API 문서에 명시한다.

```
1. 알 수 없는 필드는 무시할 것 (Robustness Principle)
2. enum 값은 화이트리스트가 아닌 폴백 처리할 것
3. 응답 필드 순서에 의존하지 말 것
4. HTTP 상태 코드의 범위(2xx, 4xx, 5xx)로 분기할 것
5. Deprecation, Sunset 헤더를 모니터링할 것
```

### 4.4 호환성 검증 자동화

```yaml
# CI/CD 파이프라인에 포함
api-compatibility-check:
  steps:
    - name: OpenAPI Spec Diff
      tool: oasdiff
      rules:
        - breaking-changes: block-merge
        - deprecation-without-sunset: block-merge
        - new-required-param: block-merge

    - name: Contract Test
      tool: pact / dredd
      rules:
        - v1-contract-violation: block-deploy
        - v2-contract-violation: block-deploy

    - name: Response Schema Validation
      tool: ajv / json-schema
      rules:
        - additional-properties: allow
        - missing-required-field: block-deploy
```

---

## 5. 필드 변경 시 구체적 마이그레이션 패턴

### 5.1 패턴 A: 필드 이름 변경

**상황:** `user_name`을 `username`으로 변경

```
v1 응답 (유지):
{
  "user_name": "john_doe"
}

v2 응답 (신규):
{
  "username": "john_doe"
}

전환 기간 (선택적, v2에서):
{
  "username": "john_doe",
  "user_name": "john_doe"    // deprecated, 다음 minor에서 제거 예고
}
```

**서버 구현:**

```python
# Adapter Layer
class UserResponseV1:
    def serialize(self, user):
        return {"user_name": user.username}

class UserResponseV2:
    def serialize(self, user):
        return {"username": user.username}
```

### 5.2 패턴 B: 필드 타입 변경

**상황:** `price`가 정수(센트 단위)에서 객체(금액+통화)로 변경

```
v1 응답:
{
  "price": 1500
}

v2 응답:
{
  "price": {
    "amount": "15.00",
    "currency": "USD"
  }
}
```

**서버 구현:**

```python
class PaymentResponseV1:
    def serialize(self, payment):
        return {
            "price": payment.amount_cents  # 정수 (센트)
        }

class PaymentResponseV2:
    def serialize(self, payment):
        return {
            "price": {
                "amount": str(payment.amount_cents / 100),  # 문자열 (소수점)
                "currency": payment.currency                 # ISO 4217
            }
        }
```

### 5.3 패턴 C: 중첩 구조 변경 (Flatten/Nest)

**상황:** 평면 구조를 중첩 구조로 변경

```
v1 응답:
{
  "user_id": 123,
  "user_email": "john@example.com",
  "user_address_city": "Seoul",
  "user_address_zip": "06100"
}

v2 응답:
{
  "id": 123,
  "email": "john@example.com",
  "address": {
    "city": "Seoul",
    "zip_code": "06100"
  }
}
```

**서버 구현:**

```python
class UserResponseV1:
    def serialize(self, user):
        return {
            "user_id": user.id,
            "user_email": user.email,
            "user_address_city": user.address.city,
            "user_address_zip": user.address.zip_code,
        }

class UserResponseV2:
    def serialize(self, user):
        return {
            "id": user.id,
            "email": user.email,
            "address": {
                "city": user.address.city,
                "zip_code": user.address.zip_code,
            },
        }
```

### 5.4 패턴 D: 리소스 분리 (Resource Splitting)

**상황:** 하나의 리소스가 두 개로 분리

```
v1:
GET /v1/users/123
Response:
{
  "id": 123,
  "name": "John",
  "payment_method": "card",
  "card_last_four": "1234"
}

v2:
GET /v2/users/123
Response:
{
  "id": 123,
  "name": "John",
  "payment_methods_url": "/v2/users/123/payment-methods"
}

GET /v2/users/123/payment-methods
Response:
{
  "items": [
    {
      "type": "card",
      "last_four": "1234"
    }
  ]
}
```

**마이그레이션 지원:**

```
v2 초기에는 편의를 위해 expand 파라미터를 지원한다:

GET /v2/users/123?expand=payment_methods
Response:
{
  "id": 123,
  "name": "John",
  "payment_methods_url": "/v2/users/123/payment-methods",
  "payment_methods": {
    "items": [
      {
        "type": "card",
        "last_four": "1234"
      }
    ]
  }
}
```

### 5.5 패턴 E: 필드 삭제

**상황:** 더 이상 제공하지 않는 필드를 제거

```
v1 응답 (유지):
{
  "id": 123,
  "name": "John",
  "legacy_score": 85    // 제거 대상
}

v2 응답:
{
  "id": 123,
  "name": "John"
  // legacy_score 필드 없음
}
```

**v1에서 선행 조치 (Deprecation 힌트):**

```http
HTTP/1.1 200 OK
X-Deprecated-Fields: legacy_score

{
  "id": 123,
  "name": "John",
  "legacy_score": 85
}
```

### 5.6 패턴 F: 에러 응답 구조 변경

```
v1 에러:
{
  "error": "invalid_email",
  "message": "The email format is invalid."
}

v2 에러 (RFC 7807 Problem Details 채택):
{
  "type": "https://api.example.com/errors/validation",
  "title": "Validation Error",
  "status": 400,
  "detail": "The email format is invalid.",
  "errors": [
    {
      "field": "email",
      "code": "invalid_format",
      "message": "Must be a valid email address."
    }
  ]
}
```

### 5.7 버전별 Adapter 구조 (코드 아키텍처)

```
src/
├── api/
│   ├── v1/
│   │   ├── routes.py
│   │   ├── serializers.py      # v1 응답 변환
│   │   └── request_parsers.py  # v1 요청 파싱
│   ├── v2/
│   │   ├── routes.py
│   │   ├── serializers.py      # v2 응답 변환
│   │   └── request_parsers.py  # v2 요청 파싱
│   └── shared/
│       └── middleware.py       # Deprecation 헤더, 버전 로깅
├── services/                   # 비즈니스 로직 (버전 무관)
│   ├── user_service.py
│   └── payment_service.py
└── models/                     # 내부 도메인 모델 (최신 구조)
    ├── user.py
    └── payment.py
```

**핵심 원칙:**
- 내부 도메인 모델은 항상 최신 구조를 따른다
- 각 API 버전의 Serializer가 도메인 모델을 해당 버전의 응답 형식으로 변환한다
- 비즈니스 로직(Service)은 버전과 무관하게 하나만 유지한다
- v1 Serializer는 최신 도메인 모델에서 v1 형식으로 역변환하는 책임을 갖는다

---

## 요약: 핵심 의사결정 정리

| 항목 | 결정 |
|------|------|
| 버전 식별 | URL Path (`/v1/`, `/v2/`) |
| 동시 운영 버전 수 | 최대 2개 |
| v1 Deprecation 기간 | v2 GA 후 24주 (약 6개월) |
| Deprecation 표시 | RFC 8594 헤더 + 커스텀 경고 헤더 |
| Sunset 응답 | 410 Gone + 마이그레이션 안내 |
| 호환성 검증 | CI/CD에서 OpenAPI diff + Contract Test |
| 코드 구조 | 버전별 Adapter + 공유 Service Layer |
| 파트너 관리 | 3-Tier 분류, 단계별 커뮤니케이션 |
| Rate Limit 축소 | Sunset Warning 기간에 점진적 축소 |
