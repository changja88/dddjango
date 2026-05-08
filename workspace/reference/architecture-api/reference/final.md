# REST API 설계 종합 가이드

> 이 문서는 REST API 설계 원칙에 집중한다. 프레임워크 구현(DRF 등)은 다루지 않는다.
> GraphQL, gRPC, SOAP, WebSocket, HATEOAS, API Gateway는 범위 밖이다.

---

## 목차

1. [REST 아키텍처 원칙](#1-rest-아키텍처-원칙)
2. [HTTP 메서드와 멱등성](#2-http-메서드와-멱등성)
3. [URL/리소스 설계 규칙](#3-url리소스-설계-규칙)
4. [HTTP 상태 코드](#4-http-상태-코드)
5. [에러 응답 형식 (RFC 9457)](#5-에러-응답-형식-rfc-9457)
6. [HTTP 헤더와 콘텐츠 협상](#6-http-헤더와-콘텐츠-협상)
7. [인증과 인가](#7-인증과-인가)
8. [페이지네이션](#8-페이지네이션)
9. [버전 관리](#9-버전-관리)
10. [하위 호환성과 Deprecation](#10-하위-호환성과-deprecation)
11. [Rate Limiting](#11-rate-limiting)
12. [멱등성 키 (Idempotency-Key)](#12-멱등성-키-idempotency-key)
13. [OpenAPI](#13-openapi)
14. [참고 문헌](#14-참고-문헌)

---

## 1. REST 아키텍처 원칙

### 1.1 REST 정의

REST(REpresentational State Transfer)는 네트워크로 연결된 시스템 설계에 대한 아이디어 모음이다. 로이 필딩의 논문에서 처음 소개되었다.

### 1.2 구성 요소

| 구성 | 설명 | 예시 |
|------|------|------|
| **자원(Resource)** | 고유한 URI로 식별되는 모든 것 | `/users/123` |
| **행위** | HTTP 메서드 | GET, POST, PUT, PATCH, DELETE |
| **표현(Representation)** | 자원의 상태를 전달하는 형식 | JSON, XML |

### 1.3 핵심 원칙

- **무상태(Stateless)**: 요청에 필요한 모든 정보가 요청 자체에 포함. 서버는 별도 상태를 관리하지 않음
- **Client-Server 분리**: 관심사를 분리하여 독립적 진화 가능
- **자원 기반 설계**: 중간 매개체 없이 URI로 자원을 직접 식별
- **균일한 인터페이스(Uniform Interface)**: HTTP 메서드와 상태 코드의 일관된 사용

### 1.4 REST의 한계

- 공식 표준이 없다 (가이드라인일 뿐)
- 실무에서는 트레이드오프를 고려하여 균형점을 찾는 것이 중요하다

> 출처: 로이 필딩 논문, Go_Deeper/Wiki/REST&SOAP, Go_Deeper/Book/Architecture/DesigningAPIS

---

## 2. HTTP 메서드와 멱등성

### 2.1 메서드별 안전성과 멱등성

| 메서드 | 안전 | 멱등 | 용도 |
|--------|:----:|:----:|------|
| **GET** | O | O | 자원 조회. 부수효과 없음 |
| **HEAD** | O | O | GET과 동일하지만 본문 없음 |
| **OPTIONS** | O | O | 통신 옵션 확인 |
| **POST** | X | X | 자원 생성. 매번 새 자원 생성 가능 |
| **PUT** | X | O | 자원 **전체 교체**. 반복해도 같은 결과 |
| **PATCH** | X | X | 자원 **부분 수정**. 반복 시 결과 달라질 수 있음 |
| **DELETE** | X | O | 자원 삭제. 반복해도 같은 효과 |

### 2.2 PUT vs PATCH

| 구분 | PUT | PATCH |
|------|-----|-------|
| 교체 범위 | **전체** — 누락된 필드는 기본값 또는 NULL | **부분** — 전달된 필드만 수정 |
| 멱등성 | O (같은 전체 상태로 교체) | X (상대적 변경이 가능, 예: `{"views": "+1"}`) |
| 필수 필드 | 모든 필드 포함 필요 | 변경할 필드만 |

### 2.3 메서드-리소스 매트릭스

| 리소스 | POST | GET | PUT | PATCH | DELETE |
|--------|------|-----|-----|-------|--------|
| `/customers` | 새로 생성 | 전체 조회 | 일괄 교체 | — | 전체 삭제 |
| `/customers/1` | 에러 | 단건 조회 | 단건 교체 | 부분 수정 | 단건 삭제 |
| `/customers/1/orders` | 주문 생성 | 주문 목록 | — | — | — |

> 출처: RFC 9110, Microsoft REST API Design, IETF

---

## 3. URL/리소스 설계 규칙

### 3.1 명명 규칙

| 규칙 | 좋음 | 나쁨 |
|------|------|------|
| 명사 사용 (동사 아님) | `/orders` | `/create-order` |
| 복수 명사 (컬렉션) | `/customers/5` | `/customer/5` |
| 케밥 케이스, 소문자 | `/order-items` | `/orderItems`, `/order_items` |
| 후행 슬래시 없음 | `/orders` | `/orders/` |
| DB 구조 비반영 | `/products` | `/tbl_products` |

### 3.2 계층적 하위 리소스

부모-자식 관계에 슬래시를 사용한다. **3단계 이상 깊이는 피한다.**

```
GET /customers/5/orders          # 고객 5의 주문 목록
GET /customers/5/orders/10       # 고객 5의 주문 10
GET /customers/5/orders/10/items # 3단계 — 허용하되 더 깊이는 피함
```

### 3.3 필터링, 정렬, 검색 패턴

```
GET /orders?status=shipped&minCost=100      # 필터링
GET /orders?sort=-price,name                 # 정렬 (- = DESC)
GET /orders?fields=id,name,total             # 필드 선택 (sparse fieldset)
GET /orders?limit=25&offset=50               # 페이지네이션
GET /items?price=gte:10&price=lte:100        # 범위 필터
GET /products?q=keyboard                     # 검색
```

> 출처: Microsoft REST API Design, Google API Design Guide, restfulapi.net

---

## 4. HTTP 상태 코드

### 4.1 분류

| 코드 범위 | 분류 | 설명 |
|----------|------|------|
| 1xx | Informational | 요청 수신, 처리 중 (거의 사용 안 함) |
| 2xx | Successful | 요청 정상 처리 |
| 3xx | Redirection | 추가 행동 필요 |
| 4xx | Client Error | 클라이언트 오류 |
| 5xx | Server Error | 서버 오류 (재시도 시 성공할 수 있음) |

### 4.2 API에서 자주 사용하는 상태 코드

**성공 (2xx):**

| 코드 | 의미 | API 용도 |
|------|------|----------|
| 200 | OK | GET, PUT, PATCH 성공 |
| 201 | Created | POST로 자원 생성 성공. Location 헤더에 새 자원 URI |
| 202 | Accepted | 비동기 처리 접수됨 (배치, 장시간 작업) |
| 204 | No Content | DELETE 성공. 응답 본문 없음 |

**클라이언트 오류 (4xx):**

| 코드 | 의미 | API 용도 |
|------|------|----------|
| 400 | Bad Request | 잘못된 요청 형식, 유효성 검증 실패 |
| 401 | Unauthorized | **인증** 필요 (누구인지 모름) |
| 403 | Forbidden | **인가** 부족 (누구인지는 알지만 권한 없음) |
| 404 | Not Found | 자원 없음 (또는 존재를 숨기기 위해) |
| 409 | Conflict | 자원 충돌 (중복 생성, 동시 수정) |
| 422 | Unprocessable Entity | 문법은 맞지만 의미적으로 처리 불가 |
| 429 | Too Many Requests | Rate Limit 초과 |

**서버 오류 (5xx):**

| 코드 | 의미 | API 용도 |
|------|------|----------|
| 500 | Internal Server Error | 서버 문제. 애매하면 500 |
| 503 | Service Unavailable | 일시 과부하/정비. Retry-After 헤더 가능 |

### 4.3 PRG (POST/Redirect/GET) 패턴

POST 주문 후 303으로 GET 결과 페이지로 리다이렉트하여 새로고침 시 중복 주문 방지.

> 출처: Go_Deeper/Wiki/Http/StatusCode, RFC 9110

---

## 5. 에러 응답 형식 (RFC 9457)

### 5.1 Problem Details for HTTP APIs

**Content-Type**: `application/problem+json`

| 필드 | 타입 | 설명 |
|------|------|------|
| `type` | URI | 문제 유형 식별. 생략 시 `about:blank` |
| `title` | string | 문제 유형의 짧은 요약 (동일 유형이면 동일 제목) |
| `status` | integer | HTTP 상태 코드 (실제 응답과 일치) |
| `detail` | string | 이 **특정 발생**에 대한 설명 |
| `instance` | URI | 이 특정 발생의 식별자 |

### 5.2 예시

```json
HTTP/1.1 403 Forbidden
Content-Type: application/problem+json

{
  "type": "https://example.com/probs/out-of-credit",
  "title": "You do not have enough credit.",
  "status": 403,
  "detail": "Your current balance is 30, but that costs 50.",
  "instance": "/account/12345/msgs/abc",
  "balance": 30,
  "accounts": ["/account/12345", "/account/67890"]
}
```

`balance`와 `accounts`는 **확장 필드**. 문제 유형 정의에서 추가 가능. 클라이언트는 인식하지 못하는 확장 필드를 무시해야 한다.

### 5.3 핵심 규칙

- `type`은 문서화 역할을 하는 안정적 URI
- `title`은 **유형**(재사용), `detail`은 **특정 발생**
- 모든 API 에러 응답에 이 형식을 일관되게 적용

> 출처: IETF RFC 9457

---

## 6. HTTP 헤더와 콘텐츠 협상

### 6.1 표현 관련 헤더

| 헤더 | 용도 | 예시 |
|------|------|------|
| Content-Type | 미디어 타입 + 인코딩 | `application/json` |
| Content-Encoding | 압축 방식 | `gzip` |
| Content-Language | 자연 언어 | `ko` |
| Content-Length | 바이트 단위 길이 | `1024` |

### 6.2 콘텐츠 협상 (Content Negotiation)

클라이언트가 선호하는 표현을 요청하는 방식.

| 요청 헤더 | 협상 대상 |
|----------|----------|
| Accept | 미디어 타입 |
| Accept-Language | 자연 언어 |
| Accept-Encoding | 압축 방식 |

**Quality Values (q값)**: 0~1 사이 값으로 우선순위 지정. 생략 시 1.

```
Accept-Language: ko-KR,ko;q=0.9,en-US;q=0.8
```

구체적인 것이 우선한다.

### 6.3 캐시 관련 헤더

| 헤더 | 용도 |
|------|------|
| Cache-Control | 캐시 정책 (max-age, no-cache, no-store, must-revalidate) |
| ETag / If-None-Match | 해시 기반 검증 (가장 정확) |
| Last-Modified / If-Modified-Since | 날짜 기반 검증 |

**304 Not Modified**: 리소스가 변경되지 않았으면 본문 없이 304 응답. 클라이언트는 로컬 캐시 사용.

> 출처: Go_Deeper/Wiki/Http/Header, RFC 9110

---

## 7. 인증과 인가

### 7.1 인증 vs 인가

| 구분 | 인증 (Authentication) | 인가 (Authorization) |
|------|---------------------|---------------------|
| 질문 | "너는 누구인가?" | "너는 이걸 할 수 있는가?" |
| 시점 | 인가보다 먼저 | 인증 후에 수행 |
| HTTP 코드 | 401 Unauthorized | 403 Forbidden |
| 실패 시 | WWW-Authenticate 헤더로 인증 방법 안내 | 권한 부족 메시지 |

- 인증이 있어야 인가가 있다
- 401은 이름이 Unauthorized지만 실제로는 **인증(Authentication)** 오류다

### 7.2 인증 메커니즘 선택 기준

| 방식 | 적합 | 특징 |
|------|------|------|
| **API Key** | 서버 간 통신, 내부 API | 단순, 사용자 식별 불가 |
| **OAuth 2.0** | 서드파티 접근 권한 위임 | 표준화, 복잡하지만 유연 |
| **JWT (Bearer Token)** | 무상태 인증, 마이크로서비스 | 자체 포함(self-contained), 만료 관리 필요 |

### 7.3 API 요청의 보안 원칙

- **비밀 정보를 쿼리 파라미터에 담지 않는다** — URL은 서버/프록시 로그에 기록됨
- 인증 정보는 `Authorization` 헤더에 전달
- 모든 API 통신에 HTTPS 사용

> 출처: Go_Deeper/Wiki/Http/StatusCode, Go_Deeper/Wiki/OAuth, Go_Deeper/Book/Architecture/DesigningAPIS

---

## 8. 페이지네이션

### 8.1 세 가지 접근법

| 방식 | 요청 | 성능 | 데이터 일관성 | 랜덤 접근 |
|------|------|------|-------------|----------|
| **Offset** | `?limit=25&offset=50` | 대규모에서 저하 | 낮음 (삽입/삭제 시 누락/중복) | 가능 |
| **Cursor** | `?limit=25&starting_after=obj_abc` | 일정 O(1) | 높음 (고정 위치 참조) | 불가 |
| **Keyset** | `?limit=25&after_id=123` | 일정 (인덱스 활용) | 높음 | 불가 |

**성능 차이**: PostgreSQL 100만 건에서 cursor 기반이 offset 기반보다 **17배 빠름**.

### 8.2 선택 기준

| 상황 | 권장 |
|------|------|
| 소규모 데이터, 관리자 대시보드 | Offset (단순, 페이지 번호 제공) |
| 실시간 피드, 무한 스크롤, 대용량 | Cursor (일관성 + 성능) |
| 고성능 읽기 중심 API | Keyset (인덱스 활용) |

### 8.3 실전 원칙

- 인덱싱된, 불변, 유니크한 필드(타임스탬프 + ID 조합)를 커서로 사용
- 커서를 불투명하게 인코딩(base64)하여 클라이언트가 토큰으로 취급하도록
- 페이지당 100-200개 결과 권장
- 응답에 `has_more` 또는 `next_cursor` 포함

> 출처: Stripe API - Pagination, Slack API - Pagination

---

## 9. 버전 관리

### 9.1 세 가지 전략

| 전략 | 예시 | 장점 | 단점 |
|------|------|------|------|
| **URL Path** | `/api/v1/products` | 즉시 보임, 라우팅 쉬움 | REST 원칙 위반, URL 오염 |
| **Header** | `Accept-Version: v1` | 깨끗한 URL, REST 부합 | 브라우저에서 안 보임, 디버깅 어려움 |
| **Query Param** | `?version=1` | 중간 지점, 가시적 | 캐싱 복잡, 필터와 혼동 |

### 9.2 Stripe의 날짜 기반 버전 관리

- URL path: 메이저 버전 (`/v1/charges`)
- 헤더: 실제 버전 (`Stripe-Version: 2024-10-01`)
- 신규 계정은 최신 버전에 자동 고정
- 요청별 오버라이드 가능

### 9.3 실전 원칙

- 하나의 전략을 선택하고 **일관되게** 적용
- 일반 패턴: URL path로 메이저 버전, 헤더로 마이너 조정
- 버전 관리 방식을 문서화하고 마이그레이션 경로 제공

> 출처: Stripe Blog - API Versioning

---

## 10. 하위 호환성과 Deprecation

### 10.1 Breaking vs Non-Breaking Change

| 변경 유형 | Breaking? | 예시 |
|----------|:---------:|------|
| 필드 추가 (응답) | X | 새 필드 `created_at` 추가 |
| 필드 추가 (요청, 선택) | X | 선택적 파라미터 `filter` 추가 |
| 필드 제거 | **O** | 기존 `name` 필드 삭제 |
| 필드 이름 변경 | **O** | `name` → `full_name` |
| 필드 타입 변경 | **O** | `id: int` → `id: string` |
| 필수 파라미터 추가 | **O** | 새 필수 필드 `email` 추가 |
| URL 경로 변경 | **O** | `/users` → `/accounts` |
| 상태 코드 변경 | **O** | 200 → 201 |
| 에러 형식 변경 | **O** | 에러 응답 구조 변경 |

### 10.2 Deprecation 프로세스

1. **Deprecation 공지**: API 문서에 명시, 변경 이력에 기록
2. **Sunset 헤더**: 응답에 만료 날짜 포함
   ```
   Sunset: Sat, 01 Mar 2025 00:00:00 GMT
   Deprecation: true
   ```
3. **마이그레이션 기간**: 최소 6개월~1년 유지
4. **대체 API 안내**: 새 엔드포인트 또는 버전으로의 마이그레이션 가이드 제공
5. **제거**: 마이그레이션 기간 종료 후 제거

### 10.3 실전 원칙

- **추가는 자유, 제거는 금지** (Additive changes only)
- Breaking change가 필요하면 새 버전을 만든다
- 클라이언트가 인식하지 못하는 필드를 무시하도록 설계 (Robustness Principle: "보내는 것은 엄격하게, 받는 것은 관대하게")

---

## 11. Rate Limiting

### 11.1 Rate Limit 헤더

```
HTTP/2 200 OK
X-RateLimit-Limit: 60          # 윈도우 내 최대 요청 수
X-RateLimit-Remaining: 56      # 남은 요청 수
X-RateLimit-Reset: 1372700873  # 리셋 시각 (UTC epoch)
```

### 11.2 429 Too Many Requests

```
HTTP/2 429 Too Many Requests
Retry-After: 30
X-RateLimit-Remaining: 0
```

### 11.3 알고리즘 선택 기준

| 알고리즘 | 특징 | 적합 |
|---------|------|------|
| **Token Bucket** | 제어된 버스트 허용 | 퍼블릭 API 기본 |
| **Sliding Window** | 부드러움, 경계 문제 없음 | 정확한 제어 필요 |
| **Fixed Window** | 단순, 저오버헤드 | 간단한 내부 API |
| **Leaky Bucket** | 일정 출력, 버스트 없음 | 트래픽 셰이핑 |

### 11.4 실전 원칙

- 비용 큰 작업(인증, DB) **전에** rate limit 검사
- 429 응답에 항상 `Retry-After` 헤더 포함
- Rate limit 정책을 API 문서에 명확히 기재

> 출처: GitHub Docs - Rate Limits, IETF Draft - RateLimit Headers

---

## 12. 멱등성 키 (Idempotency-Key)

### 12.1 문제

POST는 멱등하지 않다. 네트워크 장애로 서버는 처리했지만 클라이언트가 응답을 못 받으면, 재시도 시 중복 생성 위험.

### 12.2 Idempotency-Key 패턴

```
POST /v1/charges
Idempotency-Key: KG5LxSFa3M4fcVng
Content-Type: application/json

{"amount": 2000, "currency": "usd"}
```

**동작 방식**:
1. 클라이언트가 고유 키 생성 (V4 UUID 권장)
2. 서버가 첫 요청의 상태 코드 + 응답 본문을 저장
3. 동일 키의 후속 요청은 저장된 결과를 반환
4. 키는 24시간 후 만료 (일반적 정책)
5. POST에만 적용 — GET, PUT, DELETE는 이미 멱등

### 12.3 실전 원칙

- 결제, 주문 생성 등 **중복이 치명적인 POST**에 필수
- 멱등성 키를 내구성 있는 저장소(DB, Redis)에 보관
- 동일 키의 동시 요청에 대한 레이스 컨디션 처리 필요

> 출처: Stripe API - Idempotent Requests, Stripe Blog - Idempotency, IETF Draft - Idempotency-Key

---

## 13. OpenAPI

### 13.1 OpenAPI란

OpenAPI(구 Swagger)는 REST API를 기술하는 표준 명세 형식이다. 2015년 스마트베어에서 리눅스 파운데이션으로 이관되면서 OpenAPI로 이름이 바뀌었다.

### 13.2 용도

- API 테스트 일부 자동화
- API 설계 조기 피드백
- API 일관성 보장
- 버전별 API 변경사항 비교
- 클라이언트 SDK 자동 생성

### 13.3 실전 원칙

- API 설계 시 OpenAPI 명세를 함께 유지하여 문서와 구현의 불일치 방지
- 명세 작성 도구(Swagger Editor, Stoplight 등) 활용

> 출처: Go_Deeper/Book/Architecture/DesigningAPIS

---

## 14. 참고 문헌

| 출처 | 다룬 내용 |
|------|---------|
| Go_Deeper/Wiki/REST&SOAP | REST 정의, 원칙, 한계 |
| Go_Deeper/Wiki/Http/StatusCode | HTTP 상태 코드, PRG 패턴, 인증/인가 |
| Go_Deeper/Wiki/Http/Header | HTTP 헤더, 콘텐츠 협상, 캐시, 쿠키 |
| Go_Deeper/Book/Architecture/DesigningAPIS | OpenAPI, API 요청 설계 |
| Microsoft REST API Design Best Practices | URL 설계, 메서드-리소스 매트릭스 |
| Google API Design Guide | 리소스 명명, 필터링/정렬 패턴 |
| IETF RFC 9457 | Problem Details (에러 응답 형식) |
| IETF RFC 9110 | HTTP 메서드 안전성/멱등성 |
| Stripe Blog / Docs | 버전 관리, 페이지네이션, 멱등성 키 |
| GitHub Docs | Rate Limiting 헤더 |
| Slack API Docs | 커서 기반 페이지네이션 |
