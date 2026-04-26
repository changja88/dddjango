# API 설계 원칙 — 내부 자료 (Go_Deeper)

> 출처: Go_Deeper/Wiki/REST&SOAP, Go_Deeper/Wiki/Http, Go_Deeper/Book/Architecture/DesigningAPIS

---

## 1. REST 아키텍처

### 1.1 REST 정의

REST(REpresentational State Transfer)는 네트워크로 연결된 시스템 설계 방법에 대한 아이디어 모음이다. 로이 필딩의 논문에서 처음 소개되었다.

- **자원(Resource)**: 모든 자원은 고유한 ID(URI)가 존재하고 서버에 저장된다
- **행위**: HTTP 메서드 (GET, POST, PUT, DELETE)
- **표현(Representation)**: 클라이언트의 요청에 서버가 JSON, XML 등의 형태로 응답

### 1.2 REST 핵심 원칙

- **무상태(Stateless)**: 요청에 필요한 모든 정보가 요청 자체에 포함. 서버는 별도 상태를 관리하지 않음
- **Client-Server 분리**: 클라이언트와 서버의 관심사를 분리
- **자원 기반 설계(ROA)**: Resource Oriented Architecture — 중간 매개체 없이 리소스를 직접 주고받음
- **URI로 자원 식별**: 각 자원은 URI에 의해 유일하게 식별 (예: `/users/123`)

### 1.3 REST의 한계

- 표준이 없다 (가이드라인일 뿐)
- 사용할 수 있는 메서드가 4개뿐이다
- RESTful하게 만들려다 보면 속도가 느려질 수 있다

### 1.4 REST vs SOAP

| 구분 | REST | SOAP |
|------|------|------|
| 방식 | 가이드라인 세트 | XML 메시징 프로토콜 |
| 무게 | 경량 | 무거움 |
| 데이터 형식 | JSON, XML 등 유연 | XML 전용 |
| 적합 | IoT, 모바일, 서버리스 | 기업 보안/트랜잭션 |
| 상태 | 무상태 | 무상태 또는 상태 유지 가능 |

> 출처: Go_Deeper/Wiki/REST&SOAP

---

## 2. HTTP 상태 코드

### 2.1 상태 코드 분류

| 코드 범위 | 분류 | 설명 |
|----------|------|------|
| 1xx | Informational | 요청이 수신되어 처리 중 (거의 사용하지 않음) |
| 2xx | Successful | 요청 정상 처리 |
| 3xx | Redirection | 추가 행동 필요 |
| 4xx | Client Error | 클라이언트 오류 |
| 5xx | Server Error | 서버 오류 |

### 2.2 주요 상태 코드

**2xx 성공:**

| 코드 | 의미 | 용도 |
|------|------|------|
| 200 | OK | 요청 성공 |
| 201 | Created | 새로운 리소스 생성됨 |
| 202 | Accepted | 요청 접수됨, 처리 미완료 (배치/비동기) |
| 204 | No Content | 성공했지만 응답 본문 없음 (예: DELETE 성공) |

**4xx 클라이언트 오류:**

| 코드 | 의미 | 용도 |
|------|------|------|
| 400 | Bad Request | 잘못된 요청 문법 |
| 401 | Unauthorized | **인증(Authentication)** 필요 (로그인 안 됨) |
| 403 | Forbidden | **인가(Authorization)** 부족 (권한 없음) |
| 404 | Not Found | 리소스 없음 (또는 권한 부족 시 존재를 숨기기 위해) |

**핵심 구분**: 401은 "누구인지 모름(인증)", 403은 "누구인지는 알지만 권한 없음(인가)"

**5xx 서버 오류:**

| 코드 | 의미 | 용도 |
|------|------|------|
| 500 | Internal Server Error | 서버 문제, 애매하면 500 |
| 503 | Service Unavailable | 일시 과부하/정비. Retry-After 헤더로 복구 시점 안내 가능 |

**핵심**: 서버 오류는 재시도하면 성공할 수도 있다.

### 2.3 리다이렉션과 PRG 패턴

- **301 Moved Permanently**: 영구 이동 (검색 엔진이 인지)
- **302 Found**: 일시 이동 (실무에서 가장 많이 사용)
- **304 Not Modified**: 캐시 리다이렉트 (본문 없음, 로컬 캐시 사용)

**PRG (POST/Redirect/GET) 패턴**: POST 주문 후 303으로 GET 결과 페이지로 리다이렉트하여 새로고침 시 중복 주문 방지.

> 출처: Go_Deeper/Wiki/Http/2_http/StatusCode

---

## 3. HTTP 헤더

### 3.1 표현 관련 헤더

| 헤더 | 용도 | 예시 |
|------|------|------|
| Content-Type | 미디어 타입 + 문자 인코딩 | `application/json`, `text/html; charset=utf-8` |
| Content-Encoding | 압축 방식 | `gzip`, `deflate`, `identity` |
| Content-Language | 자연 언어 | `ko`, `en` |
| Content-Length | 바이트 단위 길이 | `1024` |

### 3.2 콘텐츠 협상 (Content Negotiation)

클라이언트가 선호하는 표현을 요청하는 방식.

| 요청 헤더 | 협상 대상 |
|----------|----------|
| Accept | 미디어 타입 |
| Accept-Charset | 문자 인코딩 |
| Accept-Encoding | 압축 인코딩 |
| Accept-Language | 자연 언어 |

**Quality Values (q값)**: 0~1 사이 값으로 우선순위 지정. 생략 시 1.
- 예: `Accept-Language: ko-KR,ko;q=0.9,en-US;q=0.8`
- 구체적인 것이 우선한다

### 3.3 캐시 관련 헤더

| 헤더 | 용도 |
|------|------|
| Cache-Control | 캐시 정책 (max-age, no-cache, no-store, must-revalidate) |
| Last-Modified / If-Modified-Since | 날짜 기반 검증 |
| ETag / If-None-Match | 해시 기반 검증 (더 정확) |

### 3.4 인증 헤더

| 헤더 | 용도 |
|------|------|
| WWW-Authenticate | 서버가 인증 방법을 알려줌 (401 응답에 포함) |
| Authorization | 클라이언트가 인증 정보를 전달 |

### 3.5 쿠키 헤더

| 헤더 | 방향 | 용도 |
|------|------|------|
| Set-Cookie | 서버→클라이언트 | 쿠키 설정 (domain, path, secure, httpOnly) |
| Cookie | 클라이언트→서버 | 저장된 쿠키 전송 |

> 출처: Go_Deeper/Wiki/Http/2_http/Header

---

## 4. API 요청 설계

### 4.1 GET vs POST

- GET과 POST의 가장 큰 차이는 **요청 본문**의 유무
- 쿼리 파라미터의 제약: 길이 제한, 바이너리 데이터 불가
- **보안 주의**: 쿼리 파라미터는 URL의 일부이므로 서버/프록시 로그에 기록됨
  - 비밀 정보를 쿼리 파라미터에 담으면 안 된다

> 출처: Go_Deeper/Book/Architecture/DesigningAPIS/2.API 요청 준비

---

## 5. OpenAPI와 API 명세

### 5.1 OpenAPI의 용도

- API 테스트 일부 자동화
- API 설계 조기 피드백
- API 일관성 보장
- 버전별 API 변경사항 비교

### 5.2 스웨거와 OpenAPI의 관계

- 스웨거 프로젝트: UI + YAML 작성 가이드로 시작
- 2015년 스마트베어에 인수
- 명세 부분은 리눅스 파운데이션에 기부, **OpenAPI**로 이름이 바뀜

> 출처: Go_Deeper/Book/Architecture/DesigningAPIS/1.API와OpenAPI소개

---

## 6. 인증과 인가

### 6.1 인증 vs 인가

| 구분 | 인증 (Authentication) | 인가 (Authorization) |
|------|---------------------|---------------------|
| 질문 | "너는 누구인가?" | "너는 이걸 할 수 있는가?" |
| 시점 | 인가보다 먼저 | 인증 후에 수행 |
| HTTP 코드 | 401 Unauthorized | 403 Forbidden |
| 예시 | 로그인 | Admin 리소스 접근 권한 |

- 인증이 있어야 인가가 있다
- 401은 이름이 Unauthorized지만 실제로는 **인증(Authentication)** 오류다 (네이밍이 아쉬움)

> 출처: Go_Deeper/Wiki/Http/2_http/StatusCode, Go_Deeper/Wiki/OAuth
