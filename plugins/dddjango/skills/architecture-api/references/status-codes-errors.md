# HTTP 상태 코드와 에러 응답 레퍼런스

상태 코드 분류, API 주요 코드, PRG 패턴, RFC 9457 Problem Details를 정리한다.

---

## 상태 코드 분류

| 코드 범위 | 분류 | 설명 |
|----------|------|------|
| 1xx | Informational | 요청 수신, 처리 중 (거의 사용 안 함) |
| 2xx | Successful | 요청 정상 처리 |
| 3xx | Redirection | 추가 행동 필요 |
| 4xx | Client Error | 클라이언트 오류 |
| 5xx | Server Error | 서버 오류 (재시도 시 성공할 수 있음) |

---

## API에서 자주 사용하는 상태 코드

### 성공 (2xx)

| 코드 | 의미 | API 용도 |
|------|------|----------|
| 200 | OK | GET, PUT, PATCH 성공 |
| 201 | Created | POST로 자원 생성 성공. Location 헤더에 새 자원 URI |
| 202 | Accepted | 비동기 처리 접수됨 (배치, 장시간 작업) |
| 204 | No Content | DELETE 성공. 응답 본문 없음 |

### 클라이언트 오류 (4xx)

| 코드 | 의미 | API 용도 |
|------|------|----------|
| 400 | Bad Request | 잘못된 요청 형식, 유효성 검증 실패 |
| 401 | Unauthorized | **인증** 필요 (누구인지 모름) |
| 403 | Forbidden | **인가** 부족 (누구인지는 알지만 권한 없음) |
| 404 | Not Found | 자원 없음 (또는 존재를 숨기기 위해) |
| 409 | Conflict | 자원 충돌 (중복 생성, 동시 수정) |
| 422 | Unprocessable Entity | 문법은 맞지만 의미적으로 처리 불가 |
| 429 | Too Many Requests | Rate Limit 초과 |

### 서버 오류 (5xx)

| 코드 | 의미 | API 용도 |
|------|------|----------|
| 500 | Internal Server Error | 서버 문제. 애매하면 500 |
| 503 | Service Unavailable | 일시 과부하/정비. Retry-After 헤더 가능 |

---

## PRG (POST/Redirect/GET) 패턴

POST 주문 후 303으로 GET 결과 페이지로 리다이렉트하여 새로고침 시 중복 주문 방지.

---

## RFC 9457 Problem Details for HTTP APIs

**Content-Type**: `application/problem+json`

### 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `type` | URI | 문제 유형 식별. 생략 시 `about:blank` |
| `title` | string | 문제 유형의 짧은 요약 (동일 유형이면 동일 제목) |
| `status` | integer | HTTP 상태 코드 (실제 응답과 일치) |
| `detail` | string | 이 **특정 발생**에 대한 설명 |
| `instance` | URI | 이 특정 발생의 식별자 |

### JSON 예시

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

### 핵심 규칙

- `type`은 문서화 역할을 하는 안정적 URI
- `title`은 **유형**(재사용), `detail`은 **특정 발생**
- 모든 API 에러 응답에 이 형식을 일관되게 적용
