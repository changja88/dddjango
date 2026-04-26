# API 리뷰 및 리팩토링

## Part 1 -- Review

현재 API 설계에서 발견된 문제를 심각도 순으로 정리한다.

### 발견 사항

**[HTTP 메서드 오용]** -- `GET /api/posts/123/delete`는 안전(safe)하고 멱등(idempotent)해야 하는 GET 메서드로 삭제라는 부수효과를 일으킨다. GET은 자원 조회 전용이며, 삭제는 DELETE 메서드의 역할이다. 웹 크롤러나 프리페치가 이 URL을 방문하면 의도치 않게 게시물이 삭제될 수 있다.

**[URL에 동사 사용]** -- `/api/posts/123/delete`와 `/api/posts/123/like`에 동사(`delete`, `like`)가 포함되어 있다. REST에서 URL은 자원(명사)을 식별하고, 행위는 HTTP 메서드로 표현해야 한다.

**[상태 코드 미사용]** -- 모든 응답에 200을 반환하면 클라이언트가 성공과 실패를 본문을 파싱해야만 구별할 수 있다. HTTP 상태 코드는 균일한 인터페이스의 핵심 요소이며, 2xx/4xx/5xx를 의미에 맞게 사용해야 한다. 특히 POST 성공 시 201, DELETE 성공 시 204, 유효성 실패 시 422 등을 구분해야 한다.

**[비표준 에러 응답 형식]** -- `{"ok": false, "msg": "error message"}` 형식은 독자 규격이다. RFC 9457 Problem Details(`type`, `title`, `status`, `detail`, `instance`)를 사용해야 클라이언트 라이브러리가 에러를 일관되게 처리할 수 있다.

**[페이지네이션 없음]** -- 목록 엔드포인트(`GET /api/posts`)가 전체 게시물을 한 번에 반환한다. 데이터가 증가하면 응답 크기가 무한히 커져 성능이 저하되고 클라이언트가 OOM을 겪을 수 있다.

**[버전 관리 없음]** -- 버전 전략이 없으면 향후 Breaking Change 발생 시 기존 클라이언트를 깨뜨리지 않고 API를 발전시킬 방법이 없다.

**[PUT 전체 교체 강제]** -- 제목만 변경해도 모든 필드를 보내야 한다. 부분 수정이 필요한 경우 PATCH를 제공해야 한다. PUT은 전체 교체, PATCH는 부분 수정이라는 명확한 구분이 있다.

**[좋아요 동작의 GET 사용]** -- `GET /api/posts/123/like`는 서버 상태를 변경하는 동작을 안전한 메서드로 수행한다. 좋아요 추가는 POST, 취소는 DELETE가 적합하다.

**[멱등성 키 미고려]** -- 게시물 생성(`POST /api/posts`)은 네트워크 장애 시 중복 생성될 수 있으나, Idempotency-Key에 대한 고려가 없다.

### 체크리스트 검증

- [x] URL 경로에 동사 사용 -- `delete`, `like` 발견
- [x] 잘못된 HTTP 메서드 -- 삭제에 GET, 좋아요에 GET 사용
- [x] 일관되지 않은 상태 코드 -- 항상 200 반환
- [x] 비표준 에러 응답 형식 -- 독자 규격 사용
- [x] 단수 명사 컬렉션 -- 해당 없음 (`posts`로 복수 사용 중)
- [x] 목록 엔드포인트 페이지네이션 없음 -- 전체 반환
- [x] 버전 관리 전략 없음 -- 확인됨
- [x] 버전 없이 Breaking Change -- 해당 사항 없음 (현재 시점)
- [x] 쿼리 파라미터의 민감 데이터 -- 해당 없음
- [x] 중요 POST의 멱등성 처리 없음 -- 게시물 생성에 미적용

---

## Part 2 -- Refactoring

리뷰에서 발견된 모든 문제에 대한 개선안을 제시한다.

### 변경 1: 버전 관리 추가

```
[Before]
GET /api/posts

[After]
GET /api/v1/posts

[Reason] 버전 관리 원칙 -- URL path 방식으로 메이저 버전을 표기한다.
모든 엔드포인트에 /v1/ 접두사를 추가하여 향후 Breaking Change 시
기존 클라이언트를 보호하면서 새 버전(/v2/)을 도입할 수 있다.
```

### 변경 2: 삭제 엔드포인트 수정

```
[Before]
GET /api/posts/123/delete

[After]
DELETE /api/v1/posts/{id}

[Reason] HTTP 메서드 원칙 + URL 명사 규칙 -- 삭제는 DELETE 메서드의 역할이다.
URL에서 동사 "delete"를 제거하고, DELETE 메서드가 행위를 표현한다.
DELETE는 멱등하므로 재시도해도 안전하며, GET으로 삭제를 수행하면
크롤러/프리페치에 의한 의도치 않은 삭제 위험이 있다.
```

### 변경 3: 좋아요 리소스화

```
[Before]
GET /api/posts/123/like

[After]
POST   /api/v1/posts/{id}/likes   → 좋아요 추가 (201 Created)
DELETE /api/v1/posts/{id}/likes   → 좋아요 취소 (204 No Content)

[Reason] HTTP 메서드 원칙 + URL 명사 규칙 -- "like"는 동사이므로
복수 명사 "likes"를 하위 리소스로 모델링한다.
상태를 변경하는 동작에 GET을 사용하면 안전성 계약을 위반한다.
추가는 POST, 취소는 DELETE로 행위를 명확히 구분한다.
```

### 변경 4: PUT에 PATCH 추가

```
[Before]
PUT /api/posts/123   → 제목만 변경해도 전체 필드 필요

[After]
PUT   /api/v1/posts/{id}   → 전체 교체 (모든 필드 필수)
PATCH /api/v1/posts/{id}   → 부분 수정 (변경할 필드만 전송)

[Reason] PUT vs PATCH 원칙 -- PUT은 자원 전체를 교체하므로 모든 필드가
필요한 것이 맞다. 하지만 제목만 변경하는 사용 사례가 있다면 PATCH를
함께 제공해야 한다. PATCH는 전달된 필드만 수정하므로 클라이언트
부담을 줄인다.
```

### 변경 5: 페이지네이션 추가

```
[Before]
GET /api/posts   → 전체 게시물 반환

[After]
GET /api/v1/posts?limit=20&after_id={last_id}

응답:
{
  "data": [...],
  "pagination": {
    "has_more": true,
    "next_cursor": "eyJpZCI6MTAwfQ=="
  }
}

[Reason] 페이지네이션 원칙 -- 무제한 목록 반환은 데이터 증가 시
응답 시간과 메모리를 무한히 소비한다. Cursor 기반 페이지네이션은
대규모 데이터에서도 일정한 O(1) 성능을 유지하며, 실시간 데이터
삽입/삭제 시에도 누락이나 중복 없이 일관된 결과를 제공한다.
```

### 변경 6: 의미적 상태 코드 적용

```
[Before]
상태 코드: 항상 200

[After]
| 동작                  | 성공 코드 | 의미            |
|-----------------------|-----------|-----------------|
| GET /posts            | 200       | OK              |
| POST /posts           | 201       | Created         |
| GET /posts/{id}       | 200       | OK              |
| PUT /posts/{id}       | 200       | OK              |
| PATCH /posts/{id}     | 200       | OK              |
| DELETE /posts/{id}    | 204       | No Content      |
| POST /posts/{id}/likes| 201       | Created         |
| DELETE /posts/{id}/likes| 204     | No Content      |

에러 코드:
| 상황                  | 코드 | 의미                |
|-----------------------|------|---------------------|
| 잘못된 요청           | 400  | Bad Request         |
| 인증 필요             | 401  | Unauthorized        |
| 권한 부족             | 403  | Forbidden           |
| 리소스 없음           | 404  | Not Found           |
| 유효성 검증 실패      | 422  | Unprocessable Entity|
| Rate Limit 초과       | 429  | Too Many Requests   |
| 서버 오류             | 500  | Internal Server Error|

[Reason] 상태 코드 원칙 -- HTTP 상태 코드는 균일한 인터페이스의 핵심이다.
항상 200을 반환하면 클라이언트가 본문을 파싱하기 전까지 성공 여부를
알 수 없다. 의미적 상태 코드를 사용하면 HTTP 미들웨어, 로드밸런서,
모니터링 도구가 자동으로 에러를 감지하고 처리할 수 있다.
```

### 변경 7: RFC 9457 에러 형식 적용

```
[Before]
{"ok": false, "msg": "error message"}

[After]
Content-Type: application/problem+json

{
  "type": "https://api.example.com/problems/not-found",
  "title": "Resource not found.",
  "status": 404,
  "detail": "Post with id 999 does not exist.",
  "instance": "/api/v1/posts/999"
}

유효성 검증 에러 예시:
{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Validation failed.",
  "status": 422,
  "detail": "One or more fields failed validation.",
  "instance": "/api/v1/posts",
  "errors": [
    {"field": "title", "message": "Title is required."},
    {"field": "content", "message": "Content must be at least 10 characters."}
  ]
}

[Reason] RFC 9457 원칙 -- 표준 형식을 사용하면 클라이언트 라이브러리가
에러를 일관되게 파싱하고 처리할 수 있다. type URI는 에러 문서로
연결되어 개발자가 문제를 빠르게 파악할 수 있으며, errors 같은 확장 필드로
필드별 유효성 검증 결과를 전달할 수 있다.
```

### 변경 8: Idempotency-Key 적용

```
[Before]
POST /api/posts   → 멱등성 키 없음

[After]
POST /api/v1/posts
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json

{"title": "...", "content": "..."}

[Reason] 멱등성 키 원칙 -- POST는 멱등하지 않으므로 네트워크 장애 시
클라이언트가 재시도하면 게시물이 중복 생성될 수 있다.
Idempotency-Key 헤더를 지원하면 서버가 동일 키의 중복 요청을
감지하여 저장된 결과를 반환한다. V4 UUID를 사용하고 24시간 후 만료한다.
```

---

## 최종 API 설계

```
GET    /api/v1/posts                → 게시물 목록 (cursor 페이지네이션)
POST   /api/v1/posts                → 게시물 작성 (Idempotency-Key 지원)
GET    /api/v1/posts/{id}           → 게시물 조회
PUT    /api/v1/posts/{id}           → 게시물 전체 수정
PATCH  /api/v1/posts/{id}           → 게시물 부분 수정
DELETE /api/v1/posts/{id}           → 게시물 삭제
POST   /api/v1/posts/{id}/likes     → 좋아요 추가
DELETE /api/v1/posts/{id}/likes     → 좋아요 취소
```

### 요청/응답 예시

**게시물 목록 조회**
```
GET /api/v1/posts?limit=20&cursor=eyJpZCI6MTAwfQ==

200 OK
{
  "data": [
    {"id": 101, "title": "...", "content": "...", "created_at": "..."},
    ...
  ],
  "pagination": {
    "has_more": true,
    "next_cursor": "eyJpZCI6MTIwfQ=="
  }
}
```

**게시물 작성**
```
POST /api/v1/posts
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json

{"title": "New Post", "content": "Post content here."}

201 Created
Location: /api/v1/posts/124
{
  "id": 124,
  "title": "New Post",
  "content": "Post content here.",
  "created_at": "2026-04-04T12:00:00Z"
}
```

**게시물 부분 수정**
```
PATCH /api/v1/posts/124
Content-Type: application/json

{"title": "Updated Title"}

200 OK
{
  "id": 124,
  "title": "Updated Title",
  "content": "Post content here.",
  "created_at": "2026-04-04T12:00:00Z"
}
```

**게시물 삭제**
```
DELETE /api/v1/posts/124

204 No Content
```

**에러 응답**
```
DELETE /api/v1/posts/999

404 Not Found
Content-Type: application/problem+json

{
  "type": "https://api.example.com/problems/not-found",
  "title": "Resource not found.",
  "status": 404,
  "detail": "Post with id 999 does not exist.",
  "instance": "/api/v1/posts/999"
}
```

### 적용된 리팩토링 체크리스트

- [x] URL의 동사 --> 명사 기반 리소스로 변경 (`delete` 제거, `like` --> `likes`)
- [x] 잘못된 메서드 --> 올바른 HTTP 메서드로 변경 (삭제에 DELETE, 좋아요에 POST/DELETE)
- [x] 잘못된 상태 코드 --> 의미적 상태 코드로 변경 (201, 204, 4xx, 5xx)
- [x] 독자 에러 형식 --> RFC 9457 Problem Details로 변환
- [x] 단수 컬렉션 이름 --> 해당 없음 (이미 복수형 사용)
- [x] 무제한 목록 --> cursor 기반 페이지네이션 추가
- [x] 버전 관리 없음 --> URL path 방식 `/v1/` 추가
- [x] Breaking Change --> 해당 없음 (신규 설계)
- [x] URL 내 민감 데이터 --> 해당 없음
- [x] 비멱등 POST --> Idempotency-Key 헤더 지원 추가
