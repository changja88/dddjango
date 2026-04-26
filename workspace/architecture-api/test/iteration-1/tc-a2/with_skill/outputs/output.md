# User Management API Design

## 인증 방식 선택

**JWT (Bearer Token)** 를 인증 메커니즘으로 선택한다.

| 고려 방식 | 판단 |
|----------|------|
| API Key | 사용자 식별이 불가하여 부적합. 서버 간 통신에 적합한 방식 |
| OAuth 2.0 | 서드파티 위임이 불필요한 자체 사용자 관리 API에는 과도함 |
| **JWT** | 무상태 인증, 토큰 자체에 사용자 정보 포함, 역할(role) 클레임으로 인가 처리 가능 |

**보안 원칙 적용:**
- 인증 정보는 `Authorization: Bearer <token>` 헤더로 전달한다. 쿼리 파라미터에 담지 않는다.
- 모든 API 통신은 HTTPS를 사용한다.
- Access Token은 짧은 만료(15분), Refresh Token은 긴 만료(7일)로 분리한다.

---

## 리소스 식별

| 리소스 | URI | 설명 |
|--------|-----|------|
| 사용자 컬렉션 | `/v1/users` | 사용자 목록 (관리자 전용) |
| 사용자 단건 | `/v1/users/{user_id}` | 개별 사용자 |
| 인증 | `/v1/auth/signup` | 회원가입 |
| 인증 | `/v1/auth/login` | 로그인 |
| 현재 사용자 | `/v1/users/me` | 현재 인증된 사용자 프로필 |

> `/auth/signup`, `/auth/login`은 인증 행위 자체가 리소스가 아닌 액션이므로, `/auth` 네임스페이스 아래에 두어 일반 리소스 엔드포인트와 구분한다. 이는 REST 원칙의 실용적 타협으로 널리 사용되는 패턴이다.

---

## 엔드포인트 상세 설계

### 1. 회원가입

```
POST /v1/auth/signup
```

**인증**: 불필요

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secureP@ss123",
  "name": "Hong Gildong"
}
```

**Response (201 Created):**
```
Location: /v1/users/550e8400-e29b-41d4-a716-446655440000
```
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "Hong Gildong",
  "role": "user",
  "created_at": "2026-04-04T09:30:00Z"
}
```

**에러 응답:**

- 이메일 중복 (409 Conflict):
```json
{
  "type": "https://api.example.com/problems/duplicate-email",
  "title": "Email already registered.",
  "status": 409,
  "detail": "The email 'user@example.com' is already associated with an existing account.",
  "instance": "/v1/auth/signup"
}
```

- 유효성 검증 실패 (422 Unprocessable Entity):
```json
{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Validation failed.",
  "status": 422,
  "detail": "One or more fields failed validation.",
  "instance": "/v1/auth/signup",
  "errors": [
    { "field": "password", "message": "Must be at least 8 characters." },
    { "field": "email", "message": "Invalid email format." }
  ]
}
```

---

### 2. 로그인

```
POST /v1/auth/login
```

**인증**: 불필요

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secureP@ss123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 900,
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2g..."
}
```

**에러 응답:**

- 인증 실패 (401 Unauthorized):
```
WWW-Authenticate: Bearer realm="api.example.com"
```
```json
{
  "type": "https://api.example.com/problems/invalid-credentials",
  "title": "Authentication failed.",
  "status": 401,
  "detail": "The email or password is incorrect.",
  "instance": "/v1/auth/login"
}
```

> 보안을 위해 이메일이 틀렸는지, 비밀번호가 틀렸는지 구분하지 않는다. 사용자 존재 여부 노출을 방지한다.

---

### 3. 내 프로필 조회

```
GET /v1/users/me
```

**인증**: 필요 (`Authorization: Bearer <access_token>`)

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "Hong Gildong",
  "role": "user",
  "created_at": "2026-04-04T09:30:00Z",
  "updated_at": "2026-04-04T09:30:00Z"
}
```

---

### 4. 내 프로필 수정

```
PATCH /v1/users/me
```

**인증**: 필요 (`Authorization: Bearer <access_token>`)

> PATCH를 사용한다. 변경할 필드만 전달하는 부분 수정이므로 PUT(전체 교체)이 아닌 PATCH가 적합하다.

**Request:**
```json
{
  "name": "Kim Cheolsu"
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "Kim Cheolsu",
  "role": "user",
  "created_at": "2026-04-04T09:30:00Z",
  "updated_at": "2026-04-04T10:15:00Z"
}
```

---

### 5. 관리자 전용 -- 사용자 목록 조회

```
GET /v1/users
```

**인증**: 필요 (`Authorization: Bearer <access_token>`)
**인가**: `admin` 역할 필요

**쿼리 파라미터:**

| 파라미터 | 타입 | 설명 | 기본값 |
|----------|------|------|--------|
| `limit` | integer | 페이지당 결과 수 (최대 100) | 25 |
| `after` | string | 커서 (다음 페이지 시작점) | - |
| `role` | string | 역할 필터 (`user`, `admin`) | - |
| `q` | string | 이름/이메일 검색 | - |
| `sort` | string | 정렬 필드 (`created_at`, `-created_at`) | `-created_at` |

> Cursor 기반 페이지네이션을 사용한다. 관리자 대시보드에서 사용자 수가 증가해도 일관된 성능을 보장하기 위함이다. 커서는 불투명한 base64 인코딩 값을 사용한다.

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "name": "Hong Gildong",
      "role": "user",
      "created_at": "2026-04-04T09:30:00Z"
    },
    {
      "id": "660f9500-f39c-52e5-b827-557766550000",
      "email": "admin@example.com",
      "name": "Kim Admin",
      "role": "admin",
      "created_at": "2026-04-03T14:00:00Z"
    }
  ],
  "has_more": true,
  "next_cursor": "dXNlcl8xMjM0NTY3ODkw"
}
```

---

## 인증/인가 실패 응답 설계

인증(Authentication)과 인가(Authorization)는 별도 단계이며, 실패 시 각각 다른 상태 코드를 반환한다.

### 인증 실패 -- 401 Unauthorized

토큰이 없거나, 만료되었거나, 유효하지 않은 경우 반환한다.

**토큰 미제공:**
```
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer realm="api.example.com"
Content-Type: application/problem+json
```
```json
{
  "type": "https://api.example.com/problems/missing-token",
  "title": "Authentication required.",
  "status": 401,
  "detail": "This endpoint requires a valid Bearer token in the Authorization header.",
  "instance": "/v1/users/me"
}
```

**토큰 만료:**
```
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer realm="api.example.com", error="invalid_token", error_description="The token has expired"
Content-Type: application/problem+json
```
```json
{
  "type": "https://api.example.com/problems/token-expired",
  "title": "Token expired.",
  "status": 401,
  "detail": "The access token has expired. Please obtain a new token using the refresh token.",
  "instance": "/v1/users/me"
}
```

**토큰 변조/유효하지 않음:**
```
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer realm="api.example.com", error="invalid_token", error_description="The token is malformed"
Content-Type: application/problem+json
```
```json
{
  "type": "https://api.example.com/problems/invalid-token",
  "title": "Invalid token.",
  "status": 401,
  "detail": "The provided token is invalid or malformed.",
  "instance": "/v1/users/me"
}
```

> 401 응답에는 반드시 `WWW-Authenticate` 헤더를 포함하여 클라이언트에게 인증 방법을 안내한다.

### 인가 실패 -- 403 Forbidden

인증은 성공했지만 해당 리소스/행위에 대한 권한이 없는 경우 반환한다.

**일반 사용자가 관리자 전용 엔드포인트 접근:**
```
HTTP/1.1 403 Forbidden
Content-Type: application/problem+json
```
```json
{
  "type": "https://api.example.com/problems/insufficient-role",
  "title": "Insufficient permissions.",
  "status": 403,
  "detail": "This endpoint requires the 'admin' role. Your current role is 'user'.",
  "instance": "/v1/users"
}
```

**다른 사용자의 프로필 수정 시도:**
```
HTTP/1.1 403 Forbidden
Content-Type: application/problem+json
```
```json
{
  "type": "https://api.example.com/problems/resource-forbidden",
  "title": "Access denied.",
  "status": 403,
  "detail": "You do not have permission to modify this resource.",
  "instance": "/v1/users/660f9500-f39c-52e5-b827-557766550000"
}
```

---

## 엔드포인트 요약 (Method-Resource Matrix)

| Method | Endpoint | 인증 | 인가 | 상태 코드 | 설명 |
|--------|----------|:----:|:----:|-----------|------|
| POST | `/v1/auth/signup` | - | - | 201 / 409 / 422 | 회원가입 |
| POST | `/v1/auth/login` | - | - | 200 / 401 | 로그인 |
| GET | `/v1/users/me` | O | 본인 | 200 / 401 | 내 프로필 조회 |
| PATCH | `/v1/users/me` | O | 본인 | 200 / 401 / 422 | 내 프로필 수정 |
| GET | `/v1/users` | O | admin | 200 / 401 / 403 | 사용자 목록 (관리자) |

---

## 설계 근거 요약

| 결정 | 근거 |
|------|------|
| JWT Bearer Token | 무상태 인증, 역할 클레임으로 인가 처리, 마이크로서비스 확장 용이 |
| URL Path 버전 관리 (`/v1/`) | 즉시 가시적, 라우팅이 쉽고 디버깅에 유리 |
| Cursor 페이지네이션 | 사용자 수 증가 시에도 일관된 성능 보장 |
| PATCH (PUT 아닌) | 프로필 수정은 부분 필드만 변경하므로 부분 수정이 적합 |
| RFC 9457 에러 형식 | 모든 에러 응답에 일관된 구조 적용. `type` URI로 문제 유형 문서화 |
| 401 + WWW-Authenticate | 인증 실패 시 클라이언트에게 인증 방법을 표준 헤더로 안내 |
| 403 (401 아닌) | 인증은 됐지만 권한이 없는 경우 명확히 구분. 인증과 인가의 분리 |
| 로그인 실패 시 모호한 메시지 | 이메일/비밀번호 중 어느 것이 틀렸는지 구분하지 않아 사용자 존재 여부 노출 방지 |
