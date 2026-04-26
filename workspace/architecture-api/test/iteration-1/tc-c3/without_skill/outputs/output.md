# API 설계 리뷰 및 리팩토링

## 1. 현재 설계의 문제점 분석

### 1.1 HTTP 메서드 오용

| 현재 | 문제 |
|------|------|
| `GET /api/posts/123/delete` | GET은 안전한(safe) 메서드로, 서버 상태를 변경하면 안 된다. 삭제에 GET을 사용하면 크롤러, 프리페치, 브라우저 히스토리 탐색 등으로 의도치 않은 삭제가 발생할 수 있다. |
| `GET /api/posts/123/like` | 동일한 문제. 좋아요는 서버 상태 변경이므로 GET을 사용해서는 안 된다. |

### 1.2 URI에 동사 사용

`/delete`, `/like`처럼 URI에 동사를 포함하는 것은 RESTful 설계 원칙에 위배된다. URI는 리소스를 식별해야 하며, 행위는 HTTP 메서드로 표현한다.

### 1.3 PUT의 부분 수정 강제

제목만 변경해도 전체 필드를 보내야 하는 것은 PUT의 정의에는 부합하지만, 클라이언트에 불필요한 부담을 준다. 부분 수정에는 PATCH가 적합하다.

### 1.4 페이지네이션 부재

전체 게시물을 한 번에 반환하면 데이터가 증가할수록 응답 크기, 메모리 사용량, 네트워크 대역폭이 선형적으로 증가한다. 운영 환경에서 장애의 직접적 원인이 된다.

### 1.5 에러 응답 설계

- **상태 코드가 항상 200**: HTTP 상태 코드의 의미를 무시한다. 클라이언트 라이브러리, 캐시, 프록시, 모니터링 시스템 모두 상태 코드에 의존하므로 올바른 상태 코드를 반환해야 한다.
- **비표준 에러 형식**: `{"ok": false, "msg": "..."}` 형식은 자체 규약이며, RFC 7807(Problem Details)과 같은 표준을 따르지 않는다.

### 1.6 API 버전 관리 부재

버전 관리가 없으면 하위 호환성을 깨는 변경을 배포할 때 기존 클라이언트가 일괄적으로 영향을 받는다.

---

## 2. 리팩토링 결과

### 2.1 엔드포인트 설계

```
# 게시물 CRUD
GET    /api/v1/posts              → 게시물 목록 (페이지네이션 적용)
POST   /api/v1/posts              → 게시물 작성
GET    /api/v1/posts/{postId}     → 게시물 조회
PATCH  /api/v1/posts/{postId}     → 게시물 부분 수정
PUT    /api/v1/posts/{postId}     → 게시물 전체 수정
DELETE /api/v1/posts/{postId}     → 게시물 삭제

# 좋아요 (하위 리소스)
POST   /api/v1/posts/{postId}/likes    → 좋아요 추가
DELETE /api/v1/posts/{postId}/likes    → 좋아요 취소
```

### 2.2 변경 사항 요약

| 변경 전 | 변경 후 | 사유 |
|---------|---------|------|
| `GET .../delete` | `DELETE /api/v1/posts/{postId}` | HTTP 메서드 시맨틱 준수 |
| `GET .../like` | `POST .../likes` | 상태 변경은 POST, 리소스명은 명사 복수형 |
| `PUT` (전체 필드 강제) | `PATCH` 추가 | 부분 수정 지원 |
| 페이지네이션 없음 | 쿼리 파라미터로 페이지네이션 | 대량 데이터 대응 |
| 상태 코드 항상 200 | 의미에 맞는 HTTP 상태 코드 | 표준 준수, 인프라 호환성 |
| 버전 없음 | URI에 `v1` 포함 | 하위 호환성 관리 |

---

### 2.3 페이지네이션

```
GET /api/v1/posts?page=1&size=20&sort=createdAt,desc
```

**응답 예시:**

```json
{
  "data": [
    { "id": 123, "title": "제목", "author": "작성자", "createdAt": "2026-04-04T09:00:00Z" }
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "totalElements": 342,
    "totalPages": 18
  }
}
```

- 기본값: `page=1`, `size=20`
- `size`의 최대값을 설정하여 과도한 요청을 방지한다 (예: `max=100`).

---

### 2.4 HTTP 상태 코드

| 상황 | 상태 코드 |
|------|-----------|
| 목록/단건 조회 성공 | `200 OK` |
| 게시물 작성 성공 | `201 Created` |
| 수정/좋아요 성공 | `200 OK` |
| 삭제 성공 | `204 No Content` |
| 요청 데이터 유효성 실패 | `400 Bad Request` |
| 인증 실패 | `401 Unauthorized` |
| 권한 부족 | `403 Forbidden` |
| 리소스 없음 | `404 Not Found` |
| 중복 좋아요 등 충돌 | `409 Conflict` |
| 서버 내부 오류 | `500 Internal Server Error` |

---

### 2.5 에러 응답 형식 (RFC 7807 기반)

```json
{
  "type": "https://api.example.com/errors/validation-failed",
  "title": "Validation Failed",
  "status": 400,
  "detail": "제목은 1자 이상 200자 이하여야 합니다.",
  "instance": "/api/v1/posts",
  "errors": [
    {
      "field": "title",
      "reason": "size must be between 1 and 200"
    }
  ]
}
```

- `Content-Type: application/problem+json`
- `type`: 에러 유형을 식별하는 URI. 클라이언트가 에러를 프로그래밍적으로 분류하는 데 사용한다.
- `errors`: 필드 단위 유효성 검증 실패 시 배열로 상세 정보를 제공한다.

---

### 2.6 성공 응답 형식

**단건 조회/생성/수정:**

```json
{
  "data": {
    "id": 123,
    "title": "제목",
    "content": "본문",
    "author": {
      "id": 1,
      "name": "작성자"
    },
    "likeCount": 5,
    "createdAt": "2026-04-04T09:00:00Z",
    "updatedAt": "2026-04-04T10:30:00Z"
  }
}
```

**생성 시 헤더:**

```
HTTP/1.1 201 Created
Location: /api/v1/posts/124
```

**삭제:**

```
HTTP/1.1 204 No Content
(본문 없음)
```

---

### 2.7 PATCH 요청 예시

제목만 수정할 때:

```http
PATCH /api/v1/posts/123
Content-Type: application/json

{
  "title": "수정된 제목"
}
```

본문에 포함된 필드만 변경되고 나머지 필드는 유지된다.

---

### 2.8 API 버전 관리 전략

URI 경로에 버전을 포함하는 방식(`/api/v1/...`)을 채택한다.

| 방식 | 장점 | 단점 |
|------|------|------|
| **URI 경로 (채택)** | 명시적, 라우팅 단순, 디버깅 용이 | URI 변경, 리소스 식별자 오염 |
| 헤더 (`Accept: application/vnd.api.v1+json`) | URI 깔끔 | 테스트/디버깅 불편, 문서화 어려움 |
| 쿼리 파라미터 (`?version=1`) | 구현 단순 | 캐시 키 복잡, 선택적 느낌 |

운영 시 `v1`을 유지하면서 `v2`를 병행 배포하고, `v1`에 Deprecation 헤더와 Sunset 날짜를 추가하여 마이그레이션을 유도한다.

---

## 3. 추가 권장 사항

| 항목 | 권장 내용 |
|------|-----------|
| **Rate Limiting** | `429 Too Many Requests` 응답과 함께 `Retry-After` 헤더를 반환한다. |
| **인증** | `Authorization: Bearer <token>` 헤더 기반 인증을 적용한다. |
| **HATEOAS** | 응답에 관련 리소스 링크를 포함하여 클라이언트가 API를 탐색할 수 있게 한다. (선택적) |
| **ETag/조건부 요청** | 캐싱 및 동시 수정 충돌 방지를 위해 `ETag`와 `If-None-Match`/`If-Match` 헤더를 활용한다. |
| **멱등성 키** | POST 요청에 `Idempotency-Key` 헤더를 지원하여 네트워크 재시도 시 중복 생성을 방지한다. |
