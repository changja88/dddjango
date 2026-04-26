# API 설계 리뷰

## 1. URL 경로에 동사 사용 문제

REST API에서 URL은 리소스(명사)를 나타내야 하며, 행위는 HTTP 메서드로 표현해야 한다. 현재 설계는 `createUser`, `getUser`, `updateUser`, `deleteUser`, `getAllUsers`처럼 동사를 URL에 포함하고 있어 RESTful 규칙에 어긋난다.

| 현재 | 개선 |
|------|------|
| `POST /api/createUser` | `POST /api/users` |
| `GET /api/getUser/123` | `GET /api/users/123` |
| `POST /api/updateUser/123` | `PUT /api/users/123` 또는 `PATCH /api/users/123` |
| `GET /api/deleteUser/123` | `DELETE /api/users/123` |
| `GET /api/getAllUsers` | `GET /api/users` |
| `POST /api/user/123/changePassword` | `PATCH /api/users/123/password` 또는 `POST /api/users/123/password` |

## 2. HTTP 메서드 오용

- **수정에 POST 사용**: `POST /api/updateUser/123`은 수정 작업이므로 `PUT`(전체 교체) 또는 `PATCH`(부분 수정)를 사용해야 한다.
- **삭제에 GET 사용**: `GET /api/deleteUser/123`은 가장 심각한 문제다. GET 요청은 안전(safe)하고 멱등(idempotent)해야 하며 서버 상태를 변경해서는 안 된다. 브라우저 프리페치, 크롤러, 캐시 서버 등이 GET 요청을 임의로 보낼 수 있으므로, 이 설계는 의도치 않은 데이터 삭제를 유발할 수 있다. 반드시 `DELETE` 메서드를 사용해야 한다.

## 3. 리소스 이름 일관성 부족

- `user` (단수)와 `User` (대문자)가 혼용되고 있다: `/api/user/123/changePassword` vs `/api/createUser`
- REST 관례상 컬렉션 리소스는 복수형 소문자(`/users`)를 사용한다.

## 4. HTTP 상태 코드 오용

성공은 항상 200, 실패는 항상 500으로 응답하는 것은 HTTP 프로토콜의 의미를 무시하는 설계다.

**문제점:**
- 클라이언트가 상태 코드만으로 결과를 판단할 수 없어 매번 응답 본문을 파싱해야 한다.
- 모니터링 도구, 로드 밸런서, CDN 등 HTTP 인프라가 정상적으로 동작하지 않는다. 예를 들어, 500 응답이 반복되면 서버 장애로 오인하여 트래픽을 차단할 수 있다.
- 입력 오류(400)와 서버 오류(500)를 구분할 수 없다.

**개선안:**
| 상황 | 상태 코드 |
|------|-----------|
| 생성 성공 | `201 Created` |
| 조회/수정/삭제 성공 | `200 OK` |
| 삭제 성공 (본문 없음) | `204 No Content` |
| 잘못된 요청 | `400 Bad Request` |
| 인증 실패 | `401 Unauthorized` |
| 권한 없음 | `403 Forbidden` |
| 리소스 없음 | `404 Not Found` |
| 입력 유효성 실패 | `422 Unprocessable Entity` |
| 서버 내부 오류 | `500 Internal Server Error` |

## 5. 응답 형식 문제

**현재 형식:**
```json
{"success": true, "data": {...}}
{"success": false, "error": "Something went wrong"}
```

**문제점:**
- `success` 필드는 HTTP 상태 코드와 중복된다. 상태 코드를 올바르게 사용하면 불필요하다.
- 오류 메시지가 `"Something went wrong"`처럼 모호하면 클라이언트가 적절한 에러 처리를 할 수 없다.

**개선안:**

성공 응답:
```json
{
  "id": 123,
  "name": "홍길동",
  "email": "hong@example.com"
}
```

에러 응답 (RFC 7807 Problem Details 형식 권장):
```json
{
  "type": "https://api.example.com/errors/validation",
  "title": "Validation Error",
  "status": 422,
  "detail": "이메일 형식이 올바르지 않습니다.",
  "errors": [
    {
      "field": "email",
      "message": "유효한 이메일 주소를 입력해주세요."
    }
  ]
}
```

## 6. 누락된 설계 고려사항

- **페이지네이션**: `GET /api/users`에 전체 목록을 한 번에 반환하면 대량 데이터 환경에서 성능 문제가 발생한다. `?page=1&size=20` 또는 커서 기반 페이지네이션이 필요하다.
- **필터링/정렬**: `GET /api/users?role=admin&sort=created_at:desc` 같은 쿼리 파라미터 지원을 고려해야 한다.
- **API 버전 관리**: `/api/v1/users`처럼 버전을 경로에 포함하거나, 헤더(`Accept: application/vnd.api.v1+json`)로 관리해야 향후 변경에 대응할 수 있다.

## 요약

| 항목 | 심각도 | 설명 |
|------|--------|------|
| GET으로 삭제 수행 | 높음 | 크롤러/프리페치에 의한 의도치 않은 삭제 위험 |
| 상태 코드 200/500 고정 | 높음 | HTTP 인프라 오동작, 에러 분류 불가 |
| URL에 동사 포함 | 중간 | RESTful 규칙 위반, API 일관성 저하 |
| 수정에 POST 사용 | 중간 | 의미론적 부정확, 캐싱 전략 수립 어려움 |
| 모호한 에러 메시지 | 중간 | 클라이언트의 에러 처리 불가 |
| 리소스 네이밍 비일관 | 낮음 | 단/복수, 대/소문자 혼용 |
| 페이지네이션 미설계 | 낮음 | 대량 데이터 시 성능 저하 |
