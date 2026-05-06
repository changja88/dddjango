---
name: architecture-api
description: >
  This skill should be used when the user asks to "design an API",
  "design REST endpoints", "define API resources", "choose HTTP
  status codes", "design error responses", "set up pagination",
  "version an API", "handle rate limiting", "design URL structure",
  or when any REST API design, endpoint naming, request/response
  format, or API evolution decision occurs. Covers REST principles,
  HTTP methods and idempotency, URL/resource naming rules,
  status codes, error format (RFC 9457), content negotiation,
  authentication/authorization concepts, pagination patterns,
  versioning strategies, backward compatibility, rate limiting,
  and idempotency keys. Use this skill whenever API endpoints,
  response formats, or API lifecycle decisions are being discussed
  — even for seemingly simple tasks like choosing a status code
  or naming a URL path. This skill focuses on design principles
  (not framework-specific). For Django Ninja API implementation, see
  implementation-django-ninja. For database schema design, see
  architecture-db.
---

# REST API 설계 원칙

이 스킬은 특정 프레임워크에 종속되지 않는 REST API 설계 원칙을 다룬다.
Django Ninja API 구현(Schema, Router, 스로틀링)에 대해서는
implementation-django-ninja에 위임한다. 데이터베이스 스키마 설계(정규화,
인덱스)에 대해서는 architecture-db에 위임한다.

이 저장소에서 Django API 구현 예시가 필요하면 framework-neutral 설계를
먼저 제시한 뒤 Django Ninja 구현으로 연결한다. 사용자가 DRF, Django REST
Framework, Serializer, ViewSet, APIView를 요청해도 DRF 구현 예시는 만들지
않고 implementation-django-ninja에 위임해 Django Ninja 대안으로 전환한다.

**비-Django API 정밀도 가드.** 사용자가 FastAPI, Flask, Express, Spring,
Go, 또는 일반 REST처럼 Django와 무관한 API 작업을 명확히 요청하면 Django,
DRF, Django Ninja, DDD, dddjango 관점으로 끌고 가지 않는다. 이런 응답에는
dddjango 스킬 체계의 `관련 스킬 참조` 섹션을 붙이지 않는다. 필요한 API 설계
원칙만 적용하고, 프레임워크는 사용자가 지정한 것을 따른다.

**기본 요구사항 — 모든 모드에 적용:**
- 리소스는 명사, 액션은 HTTP 메서드. URL에 동사를 넣지 않는다.
- 표준 HTTP 상태 코드를 일관되게 사용한다. 모든 오류는
  RFC 9457 Problem Details 형식을 사용한다.
- 진화를 고려한 설계: 추가적 변경만 허용하고, 호환성을 깨는 변경은
  새로운 버전을 필요로 한다.

아래 섹션에서 다루는 주제를 작업할 때는 링크된 참조 파일을 읽고 상세한
규칙과 예시를 확인한다.

**참조 로딩 규칙:**
- 설계 모드: API를 제안하기 전에 관련 참조를 먼저 읽는다.
- 리뷰 모드: 리뷰 결과를 확정하기 전에 인용된 모든 원칙의 참조를 읽는다.
- 리팩터링 모드: 변경 사항을 제시하기 전에 적용된 각 패턴의 참조를 읽는다.

## 응답 구조

사용자가 Django/dddjango 맥락에서 API를 요청한 경우 응답은 다음 구조를 따른다:

1. **[주요 내용]** -- 모드에 따른 코드, 리뷰, 리팩터링 결과
2. **[관련 스킬 참조]** -- 사용자의 다음 단계를 안내하는 연결점

이 스킬은 11개의 상호 연결된 스킬 체계의 일부이다.
사용자는 현재 작업 후 어떤 스킬을 호출해야 하는지 모르는 경우가
많으므로, 관련 스킬 참조가 워크플로우의 자연스러운 연결을 만든다.
단, 명확한 비-Django 요청에서는 이 섹션을 생략한다.

When the closing section is applicable, use this exact template:
```
---
> **관련 스킬 참조:**
> - [topic] → **[skill-name]** 스킬
```

## 운영 모드

사용자의 요청에 따라 모드를 선택한다:
- **설계**: API 엔드포인트, 리소스, 응답을 처음부터 설계
- **리뷰**: 기존 API 설계의 위반 사항 평가
- **리팩터링**: 기존 API 설계 개선

의도가 모호한 경우 설계 모드를 기본으로 한다.

요청이 여러 모드에 걸치는 경우(예: "리뷰하고 리팩터링해줘"), 리뷰를 먼저
적용한 후 같은 API에 리팩터링을 적용한다.

### 설계 모드

API를 설계할 때 모든 원칙을 묵시적으로 적용한다. 다음 프로세스를 따른다:
리소스 식별 -> URL 정의 -> 메서드 선택 -> 요청/응답 설계 -> 오류 처리 계획
-> 필요에 따라 페이지네이션/버저닝/속도 제한 추가.

설계를 제안하기 전에 관련 주제 영역의 참조 파일을 읽는다.

### 리뷰 모드

잘 설계된 API를 리뷰할 때는 개선 사항을 나열하기 전에 설계가 잘된 부분을
먼저 인정한다. 부실한 설계를 리뷰할 때는 가장 영향이 큰 문제부터 집중한다.

각 발견 사항은 다음 형식으로 작성한다:

```
[원칙] — 이것이 API 사용성이나 일관성에 해를 끼치는 이유 설명
```

리뷰를 확정하기 전에 아래의 모든 항목을 검증한다. 누락된 항목이 있으면 사용자가 나중에 같은 문제를 다시 발견하게 된다.
- [ ] URL 경로에 동사가 있는가 (명사만 사용해야 함)
- [ ] 연산에 맞지 않는 HTTP 메서드
- [ ] 일관성 없거나 잘못된 상태 코드
- [ ] 누락되었거나 비표준 오류 응답 형식
- [ ] 컬렉션 리소스에 단수 명사 사용
- [ ] 목록 엔드포인트에 누락된 페이지네이션
- [ ] 버저닝 전략 없음
- [ ] 버전 변경 없는 호환성 깨는 변경
- [ ] 쿼리 파라미터에 민감한 데이터
- [ ] 중요한 POST 엔드포인트에 누락된 멱등성 처리

리뷰 결과를 확정하기 전에 인용된 모든 원칙의 참조를 읽어 정확성을 확인한다.

### 리팩터링 모드

API 설계를 리팩터링할 때 변경 전/후를 보여주고 각 변경의 이유를 명시한다.
각 변경을 특정 원칙에 연결하여 근거를 추적할 수 있게 한다. 각 변경은 다음
형식으로 작성한다:

```
[Before]
<원래 API 설계>

[After]
<개선된 API 설계>

[Reason] 원칙 — 이 변경이 API를 개선하는 이유 설명
```

변경 사항을 제시하기 전에 아래의 적용 가능한 모든 개선을 적용한다. 적용 가능한 항목을 건너뛰면 사용자가 추가 리팩토링을 해야 하므로 모두 적용한다.
- [ ] 관련 스킬 참조 포함 -- 사용자의 다음 워크플로우를 위한 스킬 연결
- [ ] URL의 동사 -> 명사 기반 리소스로 이름 변경
- [ ] 잘못된 메서드 -> 올바른 HTTP 메서드로 변경
- [ ] 잘못된 상태 코드 -> 의미에 맞는 코드로 수정
- [ ] 커스텀 오류 형식 -> RFC 9457로 변환
- [ ] 단수 컬렉션 이름 -> 복수형으로 변경
- [ ] 제한 없는 목록 엔드포인트 -> 페이지네이션 추가
- [ ] 버저닝 없음 -> 버전 전략 추가
- [ ] 호환성 깨는 변경 -> 새 버전으로 이동
- [ ] URL의 민감한 데이터 -> 헤더 또는 본문으로 이동
- [ ] 멱등성 없는 중요한 POST -> Idempotency-Key 추가

변경 사항을 제시하기 전에 적용된 각 패턴의 참조를 읽는다.

---

## 1. REST 원칙

무상태, 클라이언트-서버, 균일한 인터페이스, 리소스 기반. 리소스는 URI로
식별된다. 표현은 JSON으로 전송된다. HTTP 메서드가 액션을 전달하며, URL이
아니다.

> Reference: `references/rest-principles.md`

---

## 2. HTTP 메서드와 멱등성

7가지 메서드: GET, HEAD, OPTIONS(안전+멱등), PUT, DELETE(멱등), POST,
PATCH(둘 다 아님). PUT은 전체를 교체하고, PATCH는 부분적으로 수정한다.
메서드-리소스 매트릭스가 표준 조합을 정의한다.

> Reference: `references/http-methods.md`

---

## 3. URL과 리소스 설계

컬렉션에는 복수 명사, kebab-case 소문자, 최대 3단계 깊이. 필터링/정렬/검색은
쿼리 파라미터를 통해. 동사 금지, 후행 슬래시 금지, DB 구조 미러링 금지.

> Reference: `references/url-design.md`

---

## 4. 상태 코드와 오류 형식

2xx 성공, 4xx 클라이언트 오류, 5xx 서버 오류. 401 = 인증 필요, 403 = 금지,
409 = 충돌, 422 = 유효성 검사, 429 = 속도 제한. 모든 오류는 RFC 9457
Problem Details 형식(type/title/status/detail/instance)을 사용한다.

> Reference: `references/status-codes-errors.md`

---

## 5. 헤더와 콘텐츠 협상

Content-Type, Accept 헤더, 협상을 위한 Quality Values. 캐시 헤더
(Cache-Control, ETag, Last-Modified). 인증 헤더(Authorization,
WWW-Authenticate). 속도 제한 헤더(X-RateLimit-*).

> Reference: `references/headers.md`

---

## 6. 인증과 인가

인증(Auth, 당신은 누구인가, 401) 대 인가(Authz, 이것을 할 수 있는가, 403).
서버 간 통신에 API Key, 위임에 OAuth 2.0, 무상태에 JWT. 쿼리 파라미터에
시크릿을 넣지 않는다.

> Reference: `references/auth.md`

---

## 7. 페이지네이션

Offset(단순, 성능 저하), Cursor(일관성, 빠름), Keyset(인덱스 기반). Cursor는
1M+ 레코드에서 Offset보다 17배 빠르다. 불투명한 base64 인코딩 커서를 사용한다.
응답에 has_more를 포함한다.

> Reference: `references/pagination.md`

---

## 8. 버저닝과 디프리케이션

URL 경로(/v1/), 헤더 또는 쿼리 파라미터. Stripe의 날짜 기반 모델이 모범 사례.
추가적 변경은 비호환이 아니다. 필드 제거/이름 변경/타입 변경은 호환성을
깨는 변경이다. 디프리케이션에 Sunset 헤더. 최소 6개월 마이그레이션 기간.

> Reference: `references/versioning.md`

---

## 9. 속도 제한과 멱등성

속도 제한 헤더(X-RateLimit-*), Retry-After와 함께 429. 퍼블릭 API에
Token Bucket. 멱등하지 않은 POST 엔드포인트(결제, 주문)에 Idempotency-Key
헤더. V4 UUID, 24시간 만료, 서버 측 저장.

> Reference: `references/rate-limit-idempotency.md`

---

## 10. OpenAPI

REST API를 위한 표준 스펙 형식. 테스트 자동화, 초기 설계 피드백, 일관성,
버전 비교, SDK 생성에 활용한다. 구현과 함께 스펙을 유지한다.

> Reference: `references/openapi.md`
