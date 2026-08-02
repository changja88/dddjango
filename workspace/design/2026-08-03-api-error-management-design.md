# API 에러 관리 최종 설계

- 작성일: 2026-08-03
- 상태: 사용자 리뷰 대기
- 적용 대상: dddjango가 새로 만드는 단일 Django Ninja JSON API 표면
- 기준 사례: `/Users/hyun/Desktop/broccoli-server`
- 승인 후 대체 대상: `workspace/design/2026-07-16-error-out-centralization-design.md`

## 1. 목적

API 에러의 공통 응답 형식은 한 곳에서 유지하되, 각 바운디드 컨텍스트(이하 BC)가
자기 에러 코드와 예외 매핑을 직접 소유하도록 한다. 다음 문제를 구조적으로 막는 것이
목적이다.

1. 루트 `api.py`가 모든 BC의 예외와 에러 목록을 아는 거대 카탈로그가 되는 문제
2. 공통 패키지에 validation·retryable·problem별 Schema 파일이 계속 늘어나는 문제
3. 에러 종류마다 Schema 클래스와 handler 함수가 증식하는 문제
4. controller의 실제 오류 응답과 OpenAPI 선언이 달라지는 문제
5. domain/application/infra 계층이 Django Ninja나 HTTP 에러 계약을 알게 되는 문제
6. 같은 에러 코드의 중복, 문자열 직접 사용, BC 간 에러 계약 침범을 사람이 놓치는 문제

이 설계는 중앙에서 모든 에러 종류를 등록하는 방식이 아니다. 중앙은 공통 wire shape만
소유하고, BC는 자신의 공개 에러 언어를 소유한다. 전역 프레임워크 에러만 루트 API가
소유한다.

## 2. 최종 결정 요약

| 항목 | 결정 |
|---|---|
| 에러 식별자 | URI가 아닌 안정적인 `snake_case` 문자열 `code` |
| 표준 성격 | RFC 9457 Problem Details가 아닌 Broccoli/dddjango JSON 에러 계약 |
| 미디어 타입 | `application/json` |
| 공통 Schema | `common/ninja/response/error_out.py::ErrorOut` 정확히 하나 |
| 공통 응답 디렉터리 | 빈 `__init__.py`와 `error_out.py`만 허용 |
| 공통 필드 | `code`, `title`, `status`, `detail`, `instance` |
| BC 코드 목록 | BC당 `<Bc>ErrorCode(StrEnum)` 정확히 하나 |
| BC 응답 Schema | BC당 `<Bc>ErrorOut(ErrorOut)` 정확히 하나 |
| 에러별 Schema | 만들지 않음 |
| `Literal` | 사용하지 않음. BC `ErrorOut.code`를 BC `StrEnum`으로 제한 |
| 전역 코드 목록 | `<project_config>/api.py::GlobalErrorCode` 정확히 하나 |
| BC 예외 매핑 | `<bc>/presentation_layer/api/error_handlers.py` 한 파일이 소유 |
| 전역 예외 매핑 | `<project_config>/api.py`가 소유 |
| Pydantic/Ninja 요청 검증 | 별도 Schema·handler 없이 Ninja 기본 422 응답 그대로 반환 |
| controller 책임 | 성공 응답 선언·서비스 호출·예외 raise만 담당 |
| 오류 body 생성 | 루트 `error_response()` 한 곳에서만 수행 |
| OpenAPI | `response={status: Schema}`로만 선언. 수동 후가공 금지 |
| 재시도 표현 | `retryable` body 필드 대신 에러 `code`, HTTP status와 표준 header 사용 |

## 3. 계약 범위와 용어

### 3.1 관리 대상 에러

서버가 의도적으로 예외를 잡아 `ErrorOut`으로 변환하는 에러다.

- BC의 domain/application 공개 예외
- 인증 실패
- 인가 실패
- 일반적인 route 404
- throttling
- 일반 `HttpError`
- 일시적인 데이터베이스 경합
- 영구적인 데이터베이스 실패
- 미식별 최후방 500

관리 대상 에러는 예외 없이 `code`를 포함한다.

### 3.2 관리 대상 밖의 요청 검증 오류

Django Ninja의 요청 바인딩 과정에서 만들어지는 `ninja.errors.ValidationError` 422 응답은
`ErrorOut`으로 변환하지 않는다. 이는 사용자에게 복구 가능한 비즈니스 오류가 아니라
서버와 인하우스 클라이언트 사이의 개발 계약 위반으로 취급한다.

따라서 요청 검증 오류는 이 설계에서 유일하게 `code`를 보장하지 않는 API 오류 응답이다.
클라이언트는 그 body를 안정적인 공개 계약으로 파싱하지 않고, 개발 중 잘못된 요청을
발견하는 용도로만 사용한다.

### 3.3 에러 코드와 Python 예외의 차이

- Python 예외 타입은 서버 내부 제어 흐름이다.
- 에러 코드는 클라이언트에 공개되는 안정적인 wire 계약이다.
- 여러 내부 예외가 하나의 공개 에러 코드로 합쳐질 수 있다.
- 내부 예외 이름을 바꿔도 공개 코드가 반드시 바뀌는 것은 아니다.

## 4. 외부 wire 계약

### 4.1 공통 ErrorOut

```python
# common/ninja/response/error_out.py

from ninja import Schema


class ErrorOut(Schema):
    code: str
    title: str
    status: int
    detail: str
    instance: str | None = None
```

직렬화는 `model_dump(exclude_none=True)`를 사용한다. `instance`는 값이 없으면 body에서
생략한다. 나머지 네 필드는 항상 존재한다.

### 4.2 필드 의미

| 필드 | 계약 |
|---|---|
| `code` | 클라이언트 분기·로그·분석에 사용하는 안정적인 기계 식별자 |
| `title` | 같은 code에서 변하지 않는 짧은 설명 |
| `status` | 실제 HTTP status와 반드시 동일한 정수 |
| `detail` | 이번 발생에 대한 안전한 설명. 내부 스택·SQL·민감정보 금지 |
| `instance` | 요청 ID나 오류 발생 ID가 실제로 있을 때만 제공하는 선택 필드 |

### 4.3 BC 오류 응답 예시

```json
{
  "code": "lesson_not_found",
  "title": "Lesson not found",
  "status": 404,
  "detail": "The requested lesson does not exist."
}
```

### 4.4 전역 오류 응답 예시

```json
{
  "code": "authentication_required",
  "title": "Unauthorized",
  "status": 401,
  "detail": "Authentication is required."
}
```

### 4.5 제거되는 필드와 개념

새 표준에서는 다음을 사용하지 않는다.

- RFC 9457 `type` URI
- `about:blank`
- `application/problem+json`
- `retryable` body 필드
- `invalid-params`
- 임의 `extensions` dict
- Schema에 선언되지 않은 추가 key

재시도 여부는 별도 boolean이 아니라 에러 `code`와 HTTP 의미로 결정한다. 서비스 일시
불가는 `503 Service Unavailable`과 `Retry-After`로, 리소스·상태 충돌은 계약에 따라
구체적인 code와 `409 Conflict`로 표현할 수 있다. 영구적인 장애에는 재시도를 권고하지
않는다.

## 5. 소유권과 파일 트리

아래 트리는 에러 관리와 직접 관련된 프로덕션 파일만 나타낸다.

```text
broccoli_server/
├── settings/
├── api.py
│   # api 인스턴스
│   # GlobalErrorCode
│   # error_response()
│   # server_error_response()
│   # 전역 framework/DB/catch-all handler
│   # BC import·BC 이름·BC 매핑 없음
│
└── urls.py
    # 전체 BC를 명시적으로 조립하는 composition root
    # register_accounts_api(api)
    # register_lessons_api(api)
    # ...

common/
└── ninja/
    ├── __init__.py
    ├── authentication.py
    └── response/
        ├── __init__.py
        │   # 내용 없는 package marker
        └── error_out.py
            # ErrorOut 하나만 정의

application/
├── lessons/
│   ├── lessons_api_router.py
│   │   # register_lessons_api(api)
│   │
│   └── presentation_layer/
│       ├── api/
│       │   ├── error_handlers.py
│       │   │   # LessonsError -> LessonErrorOut
│       │   └── lesson/
│       │       └── lesson_controller.py
│       │
│       └── schema/
│           ├── __init__.py
│           └── error_out.py
│               # LessonErrorCode
│               # LessonErrorOut
│
└── <bc>/
    ├── <bc>_api_router.py
    └── presentation_layer/
        ├── api/
        │   └── error_handlers.py
        └── schema/
            └── error_out.py
                # <Bc>ErrorCode
                # <Bc>ErrorOut
```

`common/ninja/response/`의 파일 제한은 Git이 추적하는 프로덕션 Python 소스 기준이다.
`__pycache__`와 `.pyc`는 검사 대상이 아니며 저장소에 커밋하지 않는다.

HTTP 표면이나 관리 대상 BC 오류가 없는 BC에는 `error_out.py`와 `error_handlers.py`를
미리 만들지 않는다.

## 6. BC 에러 계약

### 6.1 BC당 코드 Enum 하나

```python
# application/lessons/presentation_layer/schema/error_out.py

from enum import StrEnum

from common.ninja.response.error_out import ErrorOut as CommonErrorOut


class LessonErrorCode(StrEnum):
    NOT_FOUND = "lesson_not_found"
    ALREADY_REGISTERED = "lesson_already_registered"
    SCHEDULE_CONFLICT = "lesson_schedule_conflict"


class LessonErrorOut(CommonErrorOut):
    code: LessonErrorCode
```

`LessonErrorCode`는 Enum 컨테이너 하나이고, 그 안에는 공개 에러 종류가 여러 개 들어갈 수
있다. 에러 종류마다 Enum 클래스나 Schema 클래스를 새로 만들지 않는다.

BC 디렉터리 `usage_quota`의 PascalCase 이름은 `UsageQuota`이며 클래스명은
`UsageQuotaErrorCode`, `UsageQuotaErrorOut`이 된다.

### 6.2 Literal을 사용하지 않는 이유

`Literal[LessonErrorCode.NOT_FOUND]`는 특정 응답 Schema의 code를 정확히 하나로 고정하지만,
그 정밀도를 얻으려면 에러마다 concrete Schema가 필요하다. 이 설계는 OpenAPI의 status별
code 정밀도보다 BC당 Schema 하나라는 단순성을 우선한다.

따라서 controller의 다음 선언에서 404와 409는 같은 BC ErrorOut을 사용한다.

```python
response={
    200: LessonOut,
    404: LessonErrorOut,
    409: LessonErrorOut,
}
```

생성 OpenAPI는 각 status에서 모든 `LessonErrorCode` 값을 허용하는 것으로 보인다. 실제
`status`와 `code`의 올바른 조합은 BC mapping 테스트가 고정한다. 이를 보완하려고 수동으로
OpenAPI를 후가공하지 않는다.

### 6.3 BC ErrorOut 확장 금지

현재 표준의 BC ErrorOut은 `code` 타입을 BC Enum으로 좁히는 역할만 한다. 추가 필드,
validator, alias, arbitrary extension bag을 넣지 않는다. 특정 에러에 추가 데이터가 정말
필요해지면 이 설계를 예외 처리하지 않고 별도 계약 변경으로 다시 승인받는다.

## 7. 전역 에러 계약

### 7.1 GlobalErrorCode

전역 오류는 특정 BC가 아니라 단일 API 경계가 소유하므로
`<project_config>/api.py`에 둔다. Broccoli에서 이 경로는 `broccoli_server/api.py`다.

```python
class GlobalErrorCode(StrEnum):
    AUTHENTICATION_REQUIRED = "authentication_required"
    PERMISSION_DENIED = "permission_denied"
    ROUTE_NOT_FOUND = "route_not_found"
    RATE_LIMITED = "rate_limited"
    REQUEST_ERROR = "request_error"
    SERVICE_TEMPORARILY_UNAVAILABLE = "service_temporarily_unavailable"
    INTERNAL_SERVER_ERROR = "internal_server_error"
```

초기 표준 전역 매핑은 다음과 같다.

| 예외 | code | status | 추가 계약 |
|---|---|---:|---|
| `AuthenticationError` | `authentication_required` | 401 | 없음 |
| `AuthorizationError` | `permission_denied` | 403 | 없음 |
| `Http404` | `route_not_found` | 404 | BC resource 없음과 구분 |
| `Throttled` | `rate_limited` | 429 | 가능한 경우 `Retry-After` |
| `HttpError` | `request_error` | 예외 status | 안전한 detail |
| retryable `OperationalError` | `service_temporarily_unavailable` | 503 | `Retry-After` 필수 |
| non-retryable `OperationalError` | `internal_server_error` | 500 | 원인은 로그에만 기록 |
| `IntegrityError` | `internal_server_error` | 500 | 메시지 파싱으로 409 추측 금지 |
| 미식별 `Exception` | `internal_server_error` | 500 | `logger.exception`, 고정 body |

전역 handler가 새로 필요할 때만 `GlobalErrorCode`를 추가한다. BC 에러를 이 Enum에 넣지
않는다.

### 7.2 공통 응답 변환점

```python
def error_response(
    body: ErrorOut,
    *,
    headers: dict[str, str] | None = None,
) -> Response:
    response = Response(
        body.model_dump(exclude_none=True),
        status=body.status,
        content_type="application/json",
    )
    for name, value in (headers or {}).items():
        response[name] = value
    return response
```

Schema 인스턴스가 body 전체를 소유한다. handler나 controller가 dict에 key를 추가하거나
직접 `Response`를 만들지 않는다.

미식별 예외를 안전한 500으로 닫는 helper도 루트가 소유한다.

```python
def server_error_response(request: HttpRequest, exc: Exception) -> Response:
    logger.exception("Unhandled exception at API boundary")
    return error_response(
        ErrorOut(
            code=GlobalErrorCode.INTERNAL_SERVER_ERROR,
            title="Internal server error",
            status=500,
            detail="An unexpected error occurred.",
        )
    )
```

BC handler가 자기 base exception의 새 하위 타입을 아직 매핑하지 못했을 때는
`GlobalErrorCode`를 직접 import하지 않고 이 helper를 호출한다.

### 7.3 영구 장애와 일시 장애

`OperationalError` 클래스 전체를 503으로 보지 않는다. 실제 lock, deadlock,
serialization failure처럼 재시도로 해소 가능한 시그니처만 503으로 변환한다. disk I/O,
malformed database, missing table과 같은 영구 장애는 500이다.

```text
retryable DB contention
-> 503 + service_temporarily_unavailable + Retry-After

permanent DB failure
-> 500 + internal_server_error
-> 실제 원인은 logger.exception에만 기록
```

## 8. BC 예외 매핑과 등록

### 8.1 매핑 소유

각 BC의 `presentation_layer/api/error_handlers.py`가 다음을 소유한다.

- 자기 BC의 domain/application 예외 import
- 예외에서 `<Bc>ErrorCode` 선택
- HTTP status 선택
- 안정적인 title 선택
- 외부 공개에 안전한 detail 생성
- 필요한 표준 HTTP header 생성

domain/application/infra 계층은 `ErrorOut`, `<Bc>ErrorCode`, Ninja `Response`, HTTP status를
알지 못한다.

### 8.2 handler 수

BC의 공통 base exception이 있으면 handler 하나와 명시적인 mapping 하나를 우선한다.
예외 종류마다 handler 함수를 만드는 것은 기본값이 아니다. 서로 다른 등록 방식이나 응답
동작이 실제로 필요할 때만 같은 `error_handlers.py` 안에서 추가 handler를 허용한다.

base handler가 모르는 하위 예외를 받았을 때 되던지지 않는다. 공개 매핑 누락을 로그로
남기고 전역 `internal_server_error` 응답으로 안전하게 종료한다.

### 8.3 명시적인 BC 등록

```python
# application/lessons/lessons_api_router.py

def register_lessons_api(api: NinjaExtraAPI) -> None:
    register_lessons_error_handlers(api)
    api.register_controllers(LessonController)
```

```python
# broccoli_server/urls.py

register_accounts_api(api)
register_lessons_api(api)
```

모듈 import side effect로 controller나 handler를 등록하지 않는다. `urls.py`는 전체 BC를
아는 유일한 composition root다. `api.py`는 어떤 BC가 존재하는지 모른다.

## 9. 런타임 흐름

### 9.1 BC 에러

```text
HTTP request
-> controller가 application use case 호출
-> domain/application 예외 raise
-> 해당 BC handler가 code/status/title/detail로 변환
-> <Bc>ErrorOut 생성
-> error_response()가 application/json 반환
```

### 9.2 전역 에러

```text
framework/DB/unhandled exception
-> <project_config>/api.py의 구체 handler
-> GlobalErrorCode 선택
-> 공통 ErrorOut 생성
-> error_response()가 application/json 반환
```

### 9.3 요청 검증 오류

```text
잘못된 request body/query/path
-> Django Ninja request binding 실패
-> Ninja 기본 422 응답 그대로 반환
-> ErrorOut/error_response를 통과하지 않음
```

## 10. OpenAPI 계약

1. controller는 자신이 공개할 수 있는 모든 관리 대상 오류 status를 `response={...}`에
   선언한다.
2. BC 오류 status는 해당 BC의 `<Bc>ErrorOut`을 사용한다.
3. 인증·인가 등 전역 오류 status는 공통 `ErrorOut`을 사용한다.
4. Ninja 기본 요청 검증 422를 위한 별도 ErrorOut Schema는 선언하지 않는다.
5. `openapi_extra`로 오류 response를 추가하지 않는다.
6. `get_openapi_schema` override나 별도 함수로 생성 OpenAPI를 사후 수정하지 않는다.
7. 런타임과 OpenAPI 모두 `application/json`을 사용한다.
8. 같은 BC ErrorOut을 여러 status에 선언하면서 code Enum 전체가 노출되는 것은 승인된
   단순화다.

## 11. 강력 규칙 — 결정적 백스탑 대상

아래 규칙은 의미 판단 없이 AST·파일 경로·생성 artifact로 결정할 수 있으므로 백스탑으로
강제한다. 이 불변식들은 변경 파일만이 아니라 대상 프로젝트의 전체 프로덕션 트리를
검사한다.

| 영역 | 강력 규칙 | 검사 방식 |
|---|---|---|
| 검사 범위 | 에러 아키텍처 checker는 git touched-file gating을 사용하지 않는다. | 전체 프로덕션 `.py` 순회 |
| 공통 디렉터리 | `common/ninja/response/`에는 빈 `__init__.py`, `error_out.py`만 허용한다. | 허용 경로 집합 비교 |
| 공통 Schema | 공통 `error_out.py`에는 `ErrorOut` 하나만 정의한다. | AST 클래스 정의 검사 |
| 공통 필드 | `ErrorOut` 필드는 `code/title/status/detail/instance`와 승인된 타입·필수성 그대로다. | Schema AST 검사 |
| 금지 계약 | `type`, `about:blank`, problem URI, `retryable`, `invalid-params`, `ValidationErrorOut`을 새 표준 에러 코드에서 사용하지 않는다. | 파일·필드·문자열·심볼 검사 |
| BC Enum 개수 | 관리 대상 오류가 있는 BC에는 `<Bc>ErrorCode(StrEnum)`가 정확히 하나다. | BC별 AST 개수·이름 검사 |
| BC Schema 개수 | 같은 BC에는 `<Bc>ErrorOut(CommonErrorOut)`이 정확히 하나다. | BC별 AST 개수·상속 검사 |
| BC 파일 위치 | 두 클래스는 `<bc>/presentation_layer/schema/error_out.py`에만 존재한다. | 정의 위치 검사 |
| BC Schema 형태 | `<Bc>ErrorOut`은 `code: <Bc>ErrorCode`만 재선언하고 다른 필드를 추가하지 않는다. | 클래스 필드 AST 검사 |
| 파일 증식 | `*_error_out.py`, problem별 Schema 파일, validation/retryable 전용 파일을 금지한다. | 경로 패턴 검사 |
| code 형식 | Enum 값은 소문자 snake_case다. | 정규식 검사 |
| code 고유성 | `GlobalErrorCode`와 모든 BC Enum 값은 전체 프로젝트에서 중복되지 않는다. | Enum 값 전역 집합 검사 |
| code 소비 | handler의 `code=`에 문자열 리터럴을 직접 전달하지 않는다. Enum 멤버 또는 Enum 타입으로 검증된 mapping 값만 허용한다. | 호출 keyword AST + 타입 검사 |
| 전역 Enum | `GlobalErrorCode(StrEnum)`는 `<project_config>/api.py`에 정확히 하나다. | 정의 위치·개수 검사 |
| 루트 격리 | `<project_config>/api.py`는 `application.*`을 import하지 않는다. | import AST 검사 |
| 루트 BC 지식 | `api.py`에는 BC 이름·BC 경로 분기·BC 예외 map이 없다. | BC 디렉터리명 기반 AST/문자열 검사 |
| root handler | root exception handler 대상은 승인된 framework/DB/catch-all allowlist뿐이다. | decorator/call 대상 검사 |
| 계층 방향 | domain/application/infra는 Ninja·공통 ErrorOut·BC ErrorCode를 import하지 않는다. | 계층별 import 검사 |
| BC 격리 | 한 BC는 다른 BC의 ErrorCode/ErrorOut/예외를 import하지 않는다. | import 경로와 현재 BC 비교 |
| 전역 code 소유 | BC는 `GlobalErrorCode`를 import하지 않고 매핑 누락 시 `server_error_response()`만 호출한다. | import·호출 AST 검사 |
| handler 위치 | BC exception handler는 해당 BC의 `presentation_layer/api/error_handlers.py`에만 둔다. | decorator/등록 호출 위치 검사 |
| 명시적 등록 | `<bc>_api_router.py`가 `register_<bc>_error_handlers(api)`를 명시적으로 호출한다. | 등록 함수·호출 AST 검사 |
| import side effect | 모듈 최상위에서 controller/handler 등록을 실행하지 않는다. | module-level call AST 검사 |
| Validation 통과 | `ninja.errors.ValidationError` custom handler와 validation 전용 Schema를 금지한다. | import·decorator·class 검사 |
| 단일 변환점 | `error_response()` 외부에서 관리 대상 오류용 `Response`를 직접 만들지 않는다. | Response 생성 위치 검사 |
| controller | controller는 오류용 Response·tuple을 직접 반환하지 않는다. | 반환식·호출 AST 검사 |
| OpenAPI | 오류 status는 `response={...}`에 선언하고 `openapi_extra`/사후 후가공을 쓰지 않는다. | decorator·override AST 검사 |
| catch-all | 단일 API 인스턴스에 `Exception`과 `HttpError` handler가 존재한다. | API 인스턴스별 등록 검사 |
| handler 안전성 | handler에서 bare `raise`/`raise exc`로 되던지지 않는다. | Raise AST 검사 |
| 500 정보 보호 | 500 body에 `str(exc)`, traceback, DB 메시지를 넣지 않는다. | AST와 HTTP 테스트 병행 |
| status 정합 | HTTP status와 body `status`가 같다. | TestClient 계약 테스트 |

백스탑은 syntax error나 분석 불가능한 동적 표현을 조용히 통과시키지 않는다. 분석할 수 없는
경우에는 명확한 검사 오류로 실패시키거나 의미 리뷰 대상으로 올린다.

## 12. 일반 규칙 — 설계·리뷰 판단 대상

| 영역 | 일반 규칙 |
|---|---|
| code 생성 기준 | 클라이언트가 구분해 처리하거나 안정적으로 관찰할 공개 오류일 때만 새 code를 만든다. |
| 매핑 단위 | 내부 예외 수와 공개 code 수를 일치시키지 않는다. 여러 예외를 하나의 code로 합칠 수 있다. |
| 이름 | `not_found` 같은 모호한 값보다 `lesson_not_found`처럼 의미가 드러나는 값을 우선한다. BC prefix 자체는 강제하지 않는다. |
| 안정성 | 배포한 code의 이름 변경·삭제·의미 재사용은 breaking change다. |
| title | 같은 code이면 동일한 title을 유지한다. 발생별 정보는 detail로 보낸다. |
| detail | 클라이언트와 사용자에게 안전한 정보만 포함한다. `str(exc)`를 자동으로 공개하지 않는다. |
| status | 예외 클래스명이 아니라 HTTP 의미에 따라 선택한다. |
| handler 수 | BC base handler 하나를 우선하되 실제 등록·응답 동작 차이가 있으면 같은 파일에서 추가할 수 있다. |
| 알 수 없는 BC 예외 | catch-all로 안전하게 500 처리하고 mapping 누락을 로그·테스트 실패로 드러낸다. |
| 확장 필드 | 현재 표준에서는 추가하지 않는다. 실제 요구가 생기면 별도 계약 변경으로 심사한다. |
| api.py 크기 | 줄 수를 제한하지 않는다. BC를 전혀 모르고 전역 API 정책만 갖는지가 기준이다. |
| brownfield | 이미 확립된 외부 에러 계약은 자동으로 깨지 않는다. 변경은 호환성 결정을 승인받는다. |
| 클라이언트 | code를 문자열 상수로 흩뿌리지 않고 생성·수기 Enum 한 곳에서 소비한다. |

## 13. 백스탑 소유와 변경 방향

기존 checker를 다음처럼 강화한다. 같은 판단을 여러 스크립트에 중복하지 않는다.

| checker | 최종 책임 |
|---|---|
| `check-error-centralization.py` | 공통 파일 집합·ErrorOut shape·BC Enum/Schema 개수와 위치·code 형식/중복/Enum 소비·validation 금지 |
| `check-context-isolation.py` | root API의 BC 의존·계층별 Ninja 의존·BC 간 에러 계약 import 금지 |
| `check-openapi-error-declaration.py` | 전체 트리의 `response=` 오류 선언과 `openapi_extra`·후가공 금지 |
| `check-catch-all-handler.py` | 전체 트리의 catch-all·HttpError handler·되던지기 금지 |
| 신규 `check-api-error-registration.py` | 명시적 BC registrar·handler 등록·module import side effect 금지 |

모든 checker는 다음 원칙을 따른다.

1. full-tree invariant에는 touched-file gating을 사용하지 않는다.
2. AST로 확정할 수 있는 형태만 blocker로 삼되, 분석 실패를 clean으로 오인하지 않는다.
3. 오류 메시지는 위반 파일·심볼·기대 규칙·수정 방향을 함께 출력한다.
4. 프로젝트에 관리 대상 Ninja API가 없으면 해당 규칙을 적용하지 않는다.
5. 기존 다른 API framework(DRF/plain Django/server-render)는 이 checker 범위가 아니다.

## 14. 테스트 전략

### 14.1 Schema와 Enum 단위 테스트

- BC ErrorOut이 자기 BC ErrorCode 값은 허용한다.
- 정의되지 않은 문자열 code는 거부한다.
- `instance=None`은 wire body에서 빠진다.
- 전역·BC code 값이 중복되지 않는다.

### 14.2 BC mapping 테스트

각 공개 code에 대해 최소한 다음을 고정한다.

- 입력 예외 타입
- 출력 code
- HTTP/body status
- 안정적인 title
- 민감정보가 없는 detail
- 필요한 HTTP header

모든 내부 예외마다 HTTP 테스트를 복제하지 않는다. mapping 함수 단위 테스트로 조합을
검증하고, BC별 대표 오류를 HTTP integration test로 확인한다.

### 14.3 전역 HTTP 계약 테스트

- 401 `authentication_required`
- 403 `permission_denied`
- route 404 `route_not_found`
- 429 `rate_limited`
- retryable DB 오류의 503 + `Retry-After`
- non-retryable DB 오류의 안전한 500
- 미식별 예외의 안전한 500과 서버 로그
- 모든 관리 대상 응답의 `application/json`
- 실제 HTTP status와 body status 일치

### 14.4 요청 검증 회귀 테스트

잘못된 요청이 Ninja 기본 422로 반환되고 커스텀 `ErrorOut`으로 변환되지 않는지만 확인한다.
Pydantic/Ninja의 내부 body 전체를 snapshot으로 고정하지 않는다.

### 14.5 OpenAPI 계약 테스트

- controller가 선언한 각 관리 대상 status가 생성 OpenAPI에 존재한다.
- BC 오류 status는 해당 `<Bc>ErrorOut`을 참조한다.
- 전역 오류 status는 공통 `ErrorOut`을 참조한다.
- 수동 `openapi_extra`나 사후 후가공 없이 생성된다.
- 런타임과 문서의 media type이 `application/json`이다.

## 15. 호환성과 마이그레이션

### 15.1 외부 계약 변경

Broccoli의 현재 RFC 9457 형태에서 새 계약으로 바꾸는 것은 의도적인 breaking change다.

| 기존 | 신규 |
|---|---|
| `type` URI | `code` 문자열 |
| `application/problem+json` | `application/json` |
| `about:blank` | 제거 |
| `retryable` body field | 구체 code + HTTP status, 503이면 `Retry-After` |
| `invalid-params` | Ninja 기본 422 body |
| 에러별/전역 problem catalog | 전역 Enum 1개 + BC별 Enum 1개 |

서버와 인하우스 클라이언트를 같은 계약 버전으로 함께 배포한다. `type`과 `code`를 동시에
내보내는 장기 호환 계층은 만들지 않는다. 기존 클라이언트가 동시에 남아 있어야 한다면
이 설계를 바로 구현하지 않고 API version 분리 또는 짧은 전환 기간을 별도 승인받는다.

### 15.2 Broccoli 서버 정리 대상

1. `common/ninja/response/error_out.py`를 새 `code` shape로 교체한다.
2. `common/ninja/response/validation_error_out.py`를 삭제한다.
3. `broccoli_server/api.py`에 `GlobalErrorCode`와 `error_response()`를 둔다.
4. `problem_response`, `problem`, `problem_from_slug`, `_slug`, `PROBLEM_BASE`를 제거·이름 변경한다.
5. `_DOMAIN_PROBLEMS`, `_PROBLEM_DETAILS`, `_EXCEPTION_PROBLEM_DETAILS`를 제거한다.
6. 모든 `application.*` import와 BC handler를 각 BC presentation으로 이동한다.
7. 각 HTTP BC에 단일 `<Bc>ErrorCode`, `<Bc>ErrorOut`, `error_handlers.py`를 만든다.
8. 각 BC router를 명시적 `register_<bc>_api(api)` 함수로 바꾼다.
9. `urls.py`가 모든 BC registrar를 명시적으로 호출한다.
10. Managed Copy 같은 BC path-specific response policy를 해당 BC presentation으로 이동한다.
11. 오류 OpenAPI 수동 augmentation을 제거하고 controller `response=` 선언으로 교체한다.
12. 서버와 클라이언트의 code Enum 및 계약 테스트를 함께 갱신한다.

현재 Broccoli 작업 트리에는 사용자 소유의 대규모 변경과 삭제가 있으므로 구현 시 이를
원복하거나 함께 커밋하지 않는다. 에러 마이그레이션은 그 변경 위에서 별도 diff로 식별
가능해야 한다.

### 15.3 dddjango 플러그인 정본 변경 범위

이 명세 승인 후 구현 계획은 최소한 다음 정본을 다룬다.

- `dddjango/skills/architecture-api/references/final.md`
- `dddjango/skills/implementation-django-ninja/references/final.md`
- `dddjango/skills/discipline-houserules/references/final.md`
- 해당 `SKILL.md` 핵심 운영 원칙
- Coordinator와 architect/coder/reviewer/acceptance 역할 프롬프트의 오류 계약 슬롯
- §13의 결정적 checker
- Claude/Codex 의미 미러와 corpus byte mirror
- 기존 오류 계약 관련 eval fixture와 기대값

일반 API 지식에서 RFC 9457을 삭제하는 것이 아니라, dddjango 신규 output profile이
URI Problem Details 대신 code 기반 JSON 계약을 선택한다는 우선순위를 명확히 기록한다.
기존 프로젝트의 확립된 RFC 9457 계약은 brownfield 존중 규칙으로 보존한다.

## 16. 비목표

- 모든 내부 예외를 공개 code로 만드는 것
- 에러 code를 중앙 한 파일에 모두 모으는 것
- BC끼리 ErrorCode나 ErrorOut을 공유하는 것
- 요청 검증 오류를 사용자 친화적으로 변환하는 것
- Pydantic 내부 validation body를 안정적인 계약으로 고정하는 것
- 에러별 Schema·파일·handler를 만드는 것
- 임의 확장 필드와 범용 extension bag을 지원하는 것
- 기존 RFC 9457 brownfield API를 승인 없이 자동 이주하는 것
- 줄 수만으로 `api.py`를 합격·실패시키는 것

## 17. 승인 기준

다음 문장이 모두 참이면 이 설계를 승인한다.

1. 새 dddjango 표준은 RFC 9457 URI `type`이 아니라 문자열 `code`를 사용한다.
2. 관리 대상 에러는 모두 `code/title/status/detail`을 포함한다.
3. Ninja 요청 검증 422만 이 계약 밖에 둔다.
4. 공통 response 디렉터리에는 `error_out.py` 한 production module만 둔다.
5. 공통 `ErrorOut`은 wire shape만 알고 BC code를 모른다.
6. 각 BC는 ErrorCode Enum 하나와 ErrorOut Schema 하나만 소유한다.
7. BC 에러별 `Literal` Schema를 만들지 않는다.
8. 전역 code와 handler는 루트 API가 소유한다.
9. BC 예외 매핑과 handler는 해당 BC presentation이 소유한다.
10. `api.py`에는 BC import·BC mapping·BC path 분기가 없다.
11. controller는 에러 body를 직접 만들지 않는다.
12. `response=`와 생성 OpenAPI가 실제 Schema 계약을 광고한다.
13. 구조 불변식은 touched-file이 아니라 전체 트리 백스탑으로 검사한다.
14. 서버와 인하우스 클라이언트는 breaking contract를 함께 전환한다.

## 18. 대체 관계

이 문서가 사용자 승인을 받으면 2026-07-16 `ErrorOut` 중앙 계약 설계의 다음 결정을
대체한다.

- RFC 9457 `type`/`about:blank` core profile
- `application/problem+json` runtime 계약
- validation 전용 공통 concrete Schema
- problem-specific concrete ErrorOut 증식 허용
- `retryable`/extension 중심 표현
- BC problem type URI 매핑

유지되는 핵심은 공통 `ErrorOut`의 단일 소유, domain/application의 HTTP 무지, controller의
raise-only 오류 흐름, 단일 응답 변환점, 명시적인 OpenAPI response 선언, 안전한 catch-all이다.
