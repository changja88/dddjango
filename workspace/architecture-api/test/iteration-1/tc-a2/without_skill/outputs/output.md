# User Management API Design

## 1. Authentication Strategy

**JWT (JSON Web Token) + Refresh Token** 방식을 채택한다.

| 항목 | 설정 |
|---|---|
| Access Token 유효기간 | 30분 |
| Refresh Token 유효기간 | 14일 |
| 서명 알고리즘 | RS256 |
| Access Token 전달 | `Authorization: Bearer <token>` 헤더 |
| Refresh Token 전달 | HTTP-Only Secure Cookie |

### JWT Payload 구조

```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "user",
  "iat": 1712188800,
  "exp": 1712190600
}
```

---

## 2. Endpoints

### 2.1 회원가입

```
POST /api/v1/auth/signup
```

**Request Body**

```json
{
  "email": "user@example.com",
  "password": "SecureP@ss123",
  "name": "홍길동"
}
```

**Response: 201 Created**

```json
{
  "id": "usr_abc123",
  "email": "user@example.com",
  "name": "홍길동",
  "role": "user",
  "created_at": "2026-04-04T10:00:00Z"
}
```

**Validation Rules**

| 필드 | 규칙 |
|---|---|
| email | RFC 5322 형식, 최대 254자, 중복 불가 |
| password | 최소 8자, 대문자/소문자/숫자/특수문자 중 3종 이상 포함 |
| name | 1~50자 |

---

### 2.2 로그인

```
POST /api/v1/auth/login
```

**Request Body**

```json
{
  "email": "user@example.com",
  "password": "SecureP@ss123"
}
```

**Response: 200 OK**

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

Refresh Token은 `Set-Cookie` 헤더로 전달된다.

```
Set-Cookie: refresh_token=eyJ...; HttpOnly; Secure; SameSite=Strict; Path=/api/v1/auth; Max-Age=1209600
```

---

### 2.3 토큰 갱신

```
POST /api/v1/auth/refresh
```

Cookie에 포함된 Refresh Token을 사용하여 새 Access Token을 발급한다. Request Body는 없다.

**Response: 200 OK**

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

### 2.4 로그아웃

```
POST /api/v1/auth/logout
```

**Headers:** `Authorization: Bearer <access_token>`

서버 측에서 Refresh Token을 무효화하고 Cookie를 삭제한다.

**Response: 204 No Content**

---

### 2.5 내 프로필 조회

```
GET /api/v1/users/me
```

**Headers:** `Authorization: Bearer <access_token>`

**Response: 200 OK**

```json
{
  "id": "usr_abc123",
  "email": "user@example.com",
  "name": "홍길동",
  "role": "user",
  "created_at": "2026-04-04T10:00:00Z",
  "updated_at": "2026-04-04T10:00:00Z"
}
```

---

### 2.6 내 프로필 수정

```
PATCH /api/v1/users/me
```

**Headers:** `Authorization: Bearer <access_token>`

**Request Body** (변경할 필드만 포함)

```json
{
  "name": "김철수",
  "password": "NewSecureP@ss456"
}
```

**Response: 200 OK**

```json
{
  "id": "usr_abc123",
  "email": "user@example.com",
  "name": "김철수",
  "role": "user",
  "created_at": "2026-04-04T10:00:00Z",
  "updated_at": "2026-04-04T12:00:00Z"
}
```

---

### 2.7 관리자 전용: 사용자 목록 조회

```
GET /api/v1/admin/users
```

**Headers:** `Authorization: Bearer <access_token>` (role이 `admin`인 토큰 필요)

**Query Parameters**

| 파라미터 | 타입 | 기본값 | 설명 |
|---|---|---|---|
| page | integer | 1 | 페이지 번호 |
| size | integer | 20 | 페이지당 항목 수 (최대 100) |
| sort | string | created_at:desc | 정렬 기준 |
| search | string | - | 이름/이메일 검색 |
| role | string | - | 역할 필터 (`user`, `admin`) |

**Response: 200 OK**

```json
{
  "items": [
    {
      "id": "usr_abc123",
      "email": "user@example.com",
      "name": "홍길동",
      "role": "user",
      "created_at": "2026-04-04T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total_items": 153,
    "total_pages": 8
  }
}
```

---

## 3. Error Responses

모든 에러는 동일한 구조를 따른다.

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "사람이 읽을 수 있는 메시지"
  }
}
```

### 3.1 인증(Authentication) 실패

**401 Unauthorized** -- 신원 확인 실패 시 반환한다.

| 상황 | error.code | error.message |
|---|---|---|
| 잘못된 이메일/비밀번호 | `INVALID_CREDENTIALS` | 이메일 또는 비밀번호가 올바르지 않습니다 |
| Access Token 누락 | `TOKEN_MISSING` | 인증 토큰이 필요합니다 |
| Access Token 만료 | `TOKEN_EXPIRED` | 인증 토큰이 만료되었습니다 |
| Access Token 형식 오류/서명 불일치 | `TOKEN_INVALID` | 유효하지 않은 인증 토큰입니다 |
| Refresh Token 만료/무효화됨 | `REFRESH_TOKEN_INVALID` | 다시 로그인해 주세요 |

응답 헤더:

```
WWW-Authenticate: Bearer error="invalid_token", error_description="The token has expired"
```

### 3.2 인가(Authorization) 실패

**403 Forbidden** -- 인증은 되었으나 권한이 없을 때 반환한다.

| 상황 | error.code | error.message |
|---|---|---|
| 일반 사용자가 관리자 API 접근 | `INSUFFICIENT_PERMISSION` | 해당 리소스에 접근할 권한이 없습니다 |

### 3.3 기타 공통 에러

| Status | error.code | 설명 |
|---|---|---|
| 400 Bad Request | `VALIDATION_ERROR` | 요청 본문의 필수 필드 누락 또는 형식 위반 |
| 409 Conflict | `EMAIL_ALREADY_EXISTS` | 회원가입 시 이미 등록된 이메일 |
| 404 Not Found | `RESOURCE_NOT_FOUND` | 요청한 리소스가 존재하지 않음 |
| 429 Too Many Requests | `RATE_LIMIT_EXCEEDED` | 요청 횟수 초과 |

---

## 4. Security Considerations

| 항목 | 적용 방안 |
|---|---|
| 비밀번호 저장 | bcrypt (cost factor 12) |
| Rate Limiting | 로그인 엔드포인트에 IP당 5회/분, 회원가입에 IP당 3회/분 |
| 로그인 실패 잠금 | 동일 계정 연속 10회 실패 시 30분 잠금 |
| CORS | 허용된 Origin만 명시적으로 등록 |
| 보안 헤더 | `X-Content-Type-Options: nosniff`, `Strict-Transport-Security` 등 적용 |
| 민감 정보 비노출 | 로그인 실패 시 "이메일 또는 비밀번호"로 통합 메시지 사용 (어느 쪽이 틀렸는지 구분하지 않음) |

---

## 5. Endpoint Summary

| Method | Path | Auth | Role | Description |
|---|---|---|---|---|
| POST | `/api/v1/auth/signup` | - | - | 회원가입 |
| POST | `/api/v1/auth/login` | - | - | 로그인 |
| POST | `/api/v1/auth/refresh` | Cookie | - | 토큰 갱신 |
| POST | `/api/v1/auth/logout` | Bearer | any | 로그아웃 |
| GET | `/api/v1/users/me` | Bearer | any | 프로필 조회 |
| PATCH | `/api/v1/users/me` | Bearer | any | 프로필 수정 |
| GET | `/api/v1/admin/users` | Bearer | admin | 사용자 목록 조회 |
