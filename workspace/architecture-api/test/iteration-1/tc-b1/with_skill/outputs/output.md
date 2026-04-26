# API 설계 리뷰

## 리뷰 대상

```
POST /api/createUser          → 사용자 생성
GET  /api/getUser/123         → 사용자 조회
POST /api/updateUser/123      → 사용자 수정
GET  /api/deleteUser/123      → 사용자 삭제
GET  /api/getAllUsers          → 전체 사용자 목록
POST /api/user/123/changePassword → 비밀번호 변경

응답 형식:
성공: {"success": true, "data": {...}}
실패: {"success": false, "error": "Something went wrong"}
상태 코드: 성공은 항상 200, 실패는 항상 500
```

---

## 발견 사항

### 1. URL에 동사 사용

```
[URL/리소스 설계] — URL 경로에 동사(createUser, getUser, updateUser, deleteUser, getAllUsers, changePassword)가 포함되어 있다. REST에서 리소스는 명사로 식별하고, 행위는 HTTP 메서드로 표현한다. 동사가 포함된 URL은 RPC 스타일이며, 리소스 중심의 균일한 인터페이스 원칙을 위반한다.
```

**해당 엔드포인트**: 전체 6개 모두

- `POST /api/createUser` -- "create"는 동사
- `GET /api/getUser/123` -- "get"은 동사
- `POST /api/updateUser/123` -- "update"는 동사
- `GET /api/deleteUser/123` -- "delete"는 동사
- `GET /api/getAllUsers` -- "getAll"은 동사
- `POST /api/user/123/changePassword` -- "change"는 동사

### 2. 잘못된 HTTP 메서드 사용

```
[HTTP 메서드] — 수정에 POST를, 삭제에 GET을 사용하고 있다. POST는 자원 생성 전용이고, GET은 안전한(safe) 메서드로 부수효과가 없어야 한다. 삭제를 GET으로 처리하면 크롤러나 프리페치에 의해 의도치 않은 삭제가 발생할 수 있다. 수정은 PUT(전체 교체) 또는 PATCH(부분 수정)를 사용해야 한다.
```

**해당 엔드포인트**:

- `POST /api/updateUser/123` -- 수정은 PUT 또는 PATCH를 사용해야 한다
- `GET /api/deleteUser/123` -- 삭제는 DELETE 메서드를 사용해야 한다. GET은 안전한 메서드로 서버 상태를 변경하면 안 된다

### 3. 일관되지 않고 의미 없는 상태 코드

```
[상태 코드] — 성공은 항상 200, 실패는 항상 500을 반환하는 것은 HTTP 상태 코드의 의미 체계를 무시한다. 자원 생성 성공은 201 Created, 삭제 성공은 204 No Content를 반환해야 한다. 클라이언트 잘못(유효성 실패, 인증 누락, 존재하지 않는 자원)에 500을 반환하면 클라이언트는 자신의 요청이 잘못된 것인지 서버에 문제가 있는 것인지 구분할 수 없다. 400, 401, 403, 404, 409, 422 등을 적절히 구분해야 한다.
```

**구체적 문제**:

| 상황 | 현재 | 올바른 코드 |
|------|------|------------|
| 사용자 생성 성공 | 200 | 201 Created |
| 사용자 삭제 성공 | 200 | 204 No Content |
| 존재하지 않는 사용자 | 500 | 404 Not Found |
| 유효성 검증 실패 | 500 | 400 Bad Request 또는 422 Unprocessable Entity |
| 인증 실패 | 500 | 401 Unauthorized |
| 권한 부족 | 500 | 403 Forbidden |
| 중복 사용자 생성 | 500 | 409 Conflict |

### 4. 비표준 에러 응답 형식

```
[에러 형식 / RFC 9457] — 커스텀 형식 {"success": false, "error": "Something went wrong"}을 사용하고 있다. "Something went wrong"은 클라이언트가 문제를 진단하거나 자동 처리하는 데 아무런 도움이 되지 않는다. 모든 에러는 RFC 9457 Problem Details 형식(type, title, status, detail, instance)을 사용하여 문제 유형을 식별 가능하고 기계가 읽을 수 있도록 해야 한다.
```

**현재 형식**:
```json
{"success": false, "error": "Something went wrong"}
```

**RFC 9457 형식으로 개선**:
```json
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/problem+json

{
  "type": "https://api.example.com/probs/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "The email field must be a valid email address.",
  "instance": "/users"
}
```

### 5. 컬렉션 리소스에 단수 명사 사용

```
[URL/리소스 설계] — "user"를 단수로 사용하고 있다. 컬렉션 리소스는 복수 명사(/users)를 사용해야 일관된 자원 계층 구조를 표현할 수 있다. /users는 컬렉션, /users/123은 컬렉션 내 개별 항목이라는 관계가 명확해진다.
```

### 6. 목록 엔드포인트에 페이지네이션 누락

```
[페이지네이션] — GET /api/getAllUsers는 전체 사용자를 한 번에 반환한다. 데이터가 증가하면 응답 크기가 무한정 커지고 서버 메모리와 네트워크 대역폭을 과도하게 소비한다. Cursor 기반 페이지네이션을 도입하여 limit, starting_after 파라미터를 지원하고 응답에 has_more를 포함해야 한다.
```

### 7. 버전 관리 전략 없음

```
[버전 관리] — URL 경로, 헤더, 쿼리 파라미터 중 어떤 버전 관리 전략도 적용되어 있지 않다. API가 진화할 때 기존 클라이언트와의 호환성을 보장할 방법이 없다. 최소한 URL 경로 기반 버전 관리(/api/v1/users)를 적용하여 향후 breaking change에 대비해야 한다.
```

### 8. 사용자 생성(POST)에 멱등성 처리 없음

```
[멱등성] — POST /api/createUser는 멱등하지 않다. 네트워크 장애로 클라이언트가 응답을 받지 못한 후 재시도하면 중복 사용자가 생성될 수 있다. Idempotency-Key 헤더를 지원하여 동일 키의 반복 요청에 대해 저장된 결과를 반환하도록 해야 한다.
```

### 9. 비밀번호 변경 엔드포인트 설계 문제

```
[URL/리소스 설계 + HTTP 메서드] — POST /api/user/123/changePassword는 두 가지 문제가 있다. 첫째, URL에 동사(changePassword)가 포함되어 있다. 둘째, 비밀번호 변경은 사용자 리소스의 부분 수정이므로 PATCH 또는 별도 하위 리소스(/users/123/password)에 PUT을 사용하는 것이 적절하다.
```

---

## 리뷰 체크리스트 검증

- [x] URL 경로에 동사 사용 -- **위반 발견** (항목 1)
- [x] 잘못된 HTTP 메서드 -- **위반 발견** (항목 2)
- [x] 일관되지 않거나 잘못된 상태 코드 -- **위반 발견** (항목 3)
- [x] 비표준 에러 응답 형식 -- **위반 발견** (항목 4)
- [x] 컬렉션 리소스에 단수 명사 -- **위반 발견** (항목 5)
- [x] 목록 엔드포인트에 페이지네이션 누락 -- **위반 발견** (항목 6)
- [x] 버전 관리 전략 없음 -- **위반 발견** (항목 7)
- [x] 버전 없는 breaking change -- 현재 버전 자체가 없으므로 해당 없음
- [x] 쿼리 파라미터에 민감한 데이터 -- 현재 설계에서는 해당 없음
- [x] 중요 POST 엔드포인트의 멱등성 처리 누락 -- **위반 발견** (항목 8)

---

## 개선된 설계 제안

```
POST   /api/v1/users              → 사용자 생성 (201 Created)
GET    /api/v1/users/:id           → 사용자 조회 (200 OK)
PUT    /api/v1/users/:id           → 사용자 전체 수정 (200 OK)
PATCH  /api/v1/users/:id           → 사용자 부분 수정 (200 OK)
DELETE /api/v1/users/:id           → 사용자 삭제 (204 No Content)
GET    /api/v1/users               → 사용자 목록 + 페이지네이션 (200 OK)
PUT    /api/v1/users/:id/password  → 비밀번호 변경 (200 OK)
```

**페이지네이션 적용된 목록 요청/응답**:

```
GET /api/v1/users?limit=25&starting_after=user_abc123

{
  "data": [...],
  "has_more": true,
  "next_cursor": "user_xyz789"
}
```

**에러 응답 (RFC 9457)**:

```json
HTTP/1.1 404 Not Found
Content-Type: application/problem+json

{
  "type": "https://api.example.com/probs/resource-not-found",
  "title": "Resource Not Found",
  "status": 404,
  "detail": "User with id 123 does not exist.",
  "instance": "/api/v1/users/123"
}
```

**사용자 생성 시 멱등성 키 사용**:

```
POST /api/v1/users
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json

{"name": "Hyun", "email": "hyun@example.com"}
```
