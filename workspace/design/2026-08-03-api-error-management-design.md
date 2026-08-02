# API 에러 관리 최종 설계

- 작성일: 2026-08-03
- 상태: 사용자 리뷰 대기
- 적용 대상: dddjango가 새로 만드는 단일 Django Ninja JSON API 표면
- 기준 사례: `/Users/hyun/Desktop/broccoli-server`
- 승인 후 대체 대상: `workspace/design/2026-07-16-error-out-centralization-design.md`

## 1. 목적

API 에러의 공통 응답 형식은 한 곳에서 유지하되, 각 바운디드 컨텍스트(이하 BC)가
자기 에러 코드와 구체 응답을 소유하고 controller가 application 예외를 HTTP 응답으로
직접 변환하도록 한다. 다음 문제를 구조적으로 막는 것이
목적이다.

1. 루트 `api.py`가 모든 BC의 예외와 에러 목록을 아는 거대 카탈로그가 되는 문제
2. 공통 패키지에 validation·retryable·problem별 Schema 파일이 계속 늘어나는 문제
3. 에러 종류마다 공통 파일·handler·factory 함수가 증식하는 문제
4. controller의 실제 오류 응답과 OpenAPI 선언이 달라지는 문제
5. domain/application/infra 계층이 Django Ninja나 HTTP 에러 계약을 알게 되는 문제
6. 같은 에러 코드의 중복, 문자열 직접 사용, BC 간 에러 계약 침범을 사람이 놓치는 문제

이 설계는 중앙에서 에러 종류를 등록하거나 예외를 변환하는 방식이 아니다. 공통은 BC가
사용할 wire shape 하나만 소유하고, 각 BC는 자신의 공개 에러 언어와 준비된 오류 응답을
소유한다. 알려진 BC 오류만 controller가 커스텀 `ErrorOut`으로 반환하며, 인증·인가·route
404·요청 검증·미식별 500 같은 framework 오류는 Django Ninja의 기본 처리를 사용한다.

## 2. 최종 결정 요약

| 항목 | 결정 |
|---|---|
| 에러 식별자 | URI가 아닌 안정적인 `snake_case` 문자열 `code` |
| 표준 성격 | RFC 9457 Problem Details가 아닌 Broccoli/dddjango JSON 에러 계약 |
| 미디어 타입 | `application/json` |
| 공통 Schema | `common/ninja/response/error_out.py::ErrorOut` 정확히 하나 |
| 공통 응답 디렉터리 | 빈 `__init__.py`와 `error_out.py`만 허용 |
| 공통 필드 | `code`, `title`, `status`, `detail` |
| BC 코드 목록 | BC당 `<Bc>ErrorCode(StrEnum)` 정확히 하나 |
| BC 응답 base Schema | BC당 `<Bc>ErrorOut(ErrorOut)` 정확히 하나 |
| 준비된 구체 응답 | 같은 BC의 단일 `error_out.py` 안에서 `<Bc>ErrorOut` 상속으로만 허용 |
| `Literal` | 사용하지 않음. BC `ErrorOut.code`를 BC `StrEnum`으로 제한 |
| BC 예외 매핑 | 예외가 발생할 수 있는 해당 API controller가 직접 소유 |
| framework 오류 | 별도 code·Schema·handler 없이 Django Ninja 기본 응답 사용 |
| controller 책임 | 서비스 호출, 알려진 BC 예외 catch, 준비된 ErrorOut의 `Status` 반환 |
| BC 오류 body 생성 | BC `error_out.py`의 준비된 Schema를 인자 없이 생성하거나 BC base를 직접 생성 |
| 응답 helper | `error_response()`·`server_error_response()`를 만들지 않음 |
| OpenAPI | BC 오류만 `response={status: <Bc>ErrorOut}`으로 선언. 수동 후가공 금지 |
| 재시도 표현 | `retryable` body 필드 대신 에러 `code`, HTTP status와 표준 header 사용 |

## 3. 계약 범위와 용어

### 3.1 커스텀 ErrorOut 적용 대상

클라이언트가 `code`로 구분해야 하는 BC의 공개 오류만 이 계약의 적용 대상이다.

- controller가 직접 catch하는 자기 BC의 domain/application 공개 예외
- application 호출이 반환한 명시적인 실패 Result
- 클라이언트가 구분하거나 재시도해야 해서 BC가 공개하기로 한 오류

이 오류는 해당 controller가 준비된 BC ErrorOut을 `Status(error.status, error)`로 반환한다.

### 3.2 framework 기본 오류

다음 오류는 커스텀 `ErrorOut` 적용 대상이 아니다.

- 인증 실패 401
- 인가 실패 403
- route 404
- Django Ninja 요청 검증 422
- throttling 429
- 일반 `HttpError`
- raw DB/인프라 예외
- 미식별 500

별도 `GlobalErrorCode`, 전역 ErrorOut, exception handler, catch-all을 만들지 않는다. Django
Ninja와 Django의 기본 status와 body를 그대로 사용한다. 클라이언트는 이 오류를 body의
`code`가 아니라 HTTP status로 처리하며 기본 body를 안정적인 커스텀 계약으로 파싱하지
않는다.

인증 함수는 ErrorOut을 반환하지 않는다. Django Ninja에서 인증 함수의 truthy 반환값은
`request.auth`가 되므로, 인증 실패는 `None`을 반환하거나 `AuthenticationError`를 발생시켜
기본 401 흐름을 사용한다.

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
```

네 필드는 모두 필수이며 항상 존재한다. controller가 Schema를 `Status`로 반환하면 Django
Ninja가 선언된 response Schema로 직렬화하므로 `model_dump()`나 응답 helper가 필요하지 않다.

### 4.2 필드 의미

| 필드 | 계약 |
|---|---|
| `code` | 클라이언트 분기·로그·분석에 사용하는 안정적인 기계 식별자 |
| `title` | 같은 code에서 변하지 않는 짧은 설명 |
| `status` | 실제 HTTP status와 반드시 동일한 정수 |
| `detail` | 이번 발생에 대한 안전한 설명. 내부 스택·SQL·민감정보 금지 |

### 4.3 BC 오류 응답 예시

```json
{
  "code": "lesson_not_found",
  "title": "Lesson not found",
  "status": 404,
  "detail": "The requested lesson does not exist."
}
```

### 4.4 제거되는 필드와 개념

새 표준에서는 다음을 사용하지 않는다.

- RFC 9457 `type` URI
- `about:blank`
- `application/problem+json`
- `retryable` body 필드
- `invalid-params`
- `instance`
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
│   # api 인스턴스와 API 자체 설정만 소유
│   # ErrorCode·ErrorOut·응답 helper·custom exception handler 없음
│   # application import·BC 이름·BC 매핑 없음
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
│   │   # register_lessons_api(api): controller 등록만 수행
│   │
│   └── presentation_layer/
│       ├── api/
│       │   └── lesson/
│       │       └── lesson_controller.py
│       │           # 알려진 Lesson 예외 catch
│       │           # 준비된 Lesson ErrorOut을 Status로 직접 반환
│       │
│       └── schema/
│           ├── __init__.py
│           └── error_out.py
│               # LessonErrorCode
│               # LessonErrorOut
│               # LessonNotFoundError 등 준비된 같은-shape 응답
│
└── <bc>/
    ├── <bc>_api_router.py
    └── presentation_layer/
        ├── api/
        │   └── <resource>/
        │       └── <resource>_controller.py
        └── schema/
            └── error_out.py
                # <Bc>ErrorCode
                # <Bc>ErrorOut
                # 준비된 concrete ErrorOut
```

`common/ninja/response/`의 파일 제한은 Git이 추적하는 프로덕션 Python 소스 기준이다.
`__pycache__`와 `.pyc`는 검사 대상이 아니며 저장소에 커밋하지 않는다.

HTTP 표면이나 관리 대상 BC 오류가 없는 BC에는 `error_out.py`를 미리 만들지 않는다.
`presentation_layer/api/error_handlers.py`는 어떤 BC에도 만들지 않는다.

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


class LessonNotFoundError(LessonErrorOut):
    code: LessonErrorCode = LessonErrorCode.NOT_FOUND
    title: str = "Lesson not found"
    status: int = 404
    detail: str = "The requested lesson does not exist."
```

`LessonErrorCode`는 Enum 컨테이너 하나이고, 그 안에는 공개 에러 종류가 여러 개 들어갈 수
있다. 에러 종류마다 Enum 클래스를 새로 만들지 않는다.

`LessonErrorOut`은 BC의 단일 base Schema다. `LessonNotFoundError()`처럼 고정된 값을 인자
없이 바로 반환할 필요가 있으면 같은 `error_out.py` 안에 준비된 concrete Schema를 둘 수
있다. 이 클래스는 `<Bc>ErrorOut`을 상속하고 공통 필드의 기본값만 고정한다. 새 필드,
validator, alias, 별도 파일은 추가하지 않는다. 고정된 값을 채우기 위한 `make_*`, `build_*`,
`*_error()` factory 함수도 만들지 않는다.

BC 디렉터리 `usage_quota`의 PascalCase 이름은 `UsageQuota`이며 클래스명은
`UsageQuotaErrorCode`, `UsageQuotaErrorOut`이 된다.

### 6.2 Literal을 사용하지 않는 이유

`Literal[LessonErrorCode.NOT_FOUND]`는 특정 응답 Schema의 code를 타입 수준에서 정확히
하나로 고정한다. 이 설계에서 준비된 concrete Schema는 no-argument 생성 시의 기본값을
고정하기 위한 것이지, 에러마다 서로 다른 wire shape나 `Literal` 계약을 만들기 위한 것이
아니다. code 타입은 모든 BC Schema에서 `LessonErrorCode`로 유지한다.

따라서 controller의 다음 선언에서 404와 409는 같은 BC ErrorOut을 사용한다.

```python
response={
    200: LessonOut,
    404: LessonErrorOut,
    409: LessonErrorOut,
}
```

생성 OpenAPI는 각 status에서 모든 `LessonErrorCode` 값을 허용하는 것으로 보인다. 실제
`status`와 `code`의 올바른 조합은 controller 계약 테스트가 고정한다. 이를 보완하려고
수동으로 OpenAPI를 후가공하지 않는다.

### 6.3 BC ErrorOut 확장 금지

현재 표준의 BC base ErrorOut은 `code` 타입을 BC Enum으로 좁히는 역할만 한다. 준비된
concrete ErrorOut은 기존 공통 필드의 기본값만 고정한다. 어느 쪽에도 추가 필드, validator,
alias, arbitrary extension bag을 넣지 않는다. 특정 에러에 추가 데이터가 정말 필요해지면
이 설계를 예외 처리하지 않고 별도 계약 변경으로 다시 승인받는다.

## 7. Framework 오류는 기본 처리

`broccoli_server/api.py`는 framework 오류를 커스텀 ErrorOut으로 바꾸지 않는다. Django
Ninja가 기본 등록한 `Http404`, `HttpError`, `ValidationError`, `Exception` 처리 흐름을
그대로 사용하고 `AuthenticationError`, `AuthorizationError`, `Throttled`도 기본
`HttpError` 응답을 따른다.

raw DB/인프라 예외와 미식별 예외도 controller가 잡지 않는다. Django Ninja와 Django의
기본 500 처리에 맡긴다. 클라이언트에 공개할 재시도 의미가 실제로 필요한 경우에만 infra가
자기 BC의 application/domain 예외로 정규화하고, 해당 controller가 준비된 BC ErrorOut과
필요한 표준 header를 반환한다. raw `OperationalError` 전체를 전역 503으로 추측하지 않는다.
운영 환경의 `DEBUG=False`는 Django 기본 500이 traceback을 노출하지 않기 위한 전제이며,
이를 대신하는 custom catch-all은 만들지 않는다.

따라서 다음 항목은 새 표준에 존재하지 않는다.

- `GlobalErrorCode`
- 전역 ErrorOut 또는 전역 오류 catalog
- `error_response()`와 `server_error_response()`
- `@api.exception_handler`와 `api.add_exception_handler`를 사용한 custom handler
- custom catch-all
- framework 오류 body의 수동 직렬화

## 8. BC 오류의 controller 직접 반환

### 8.1 매핑 소유

예외가 발생할 수 있는 해당 API controller가 다음을 소유한다.

- 자기 BC의 domain/application 공개 예외 catch
- 반환할 준비된 `<Bc>ErrorOut` 선택
- 실제 HTTP status와 body `status` 일치
- 필요한 표준 HTTP header 반환

에러의 `code`, `title`, `status`, `detail`이 고정되어 있으면 BC의 단일
`presentation_layer/schema/error_out.py`에 준비된 concrete Schema로 정의한다. controller는
그 Schema를 인자 없이 생성하고 `Status(error.status, error)`로 바로 반환한다. 고정값을
채우기 위한 mapping 함수, factory, BC exception handler는 만들지 않는다.

domain/application/infra 계층은 `ErrorOut`, `<Bc>ErrorCode`, Ninja `Status`/`Response`, HTTP
status를 알지 못한다.

### 8.2 controller 예시

```python
from django.http import HttpRequest
from ninja import Status
from ninja_extra import api_controller, route, status


@api_controller("/lessons", tags=["lessons"])
class LessonController:
    @route.get(
        "/{lesson_id}",
        response={
            200: LessonOut,
            404: LessonErrorOut,
        },
    )
    def get_lesson(
        self,
        request: HttpRequest,
        lesson_id: int,
    ) -> Status[LessonOut | LessonErrorOut]:
        try:
            lesson = build_get_lesson_query().execute(lesson_id)
        except LessonNotFoundException:
            error = LessonNotFoundError()
            return Status(error.status, error)

        return Status(
            status.HTTP_200_OK,
            LessonOut.from_domain(lesson),
        )
```

`try` 범위는 예외 계약을 가진 application 호출로 좁힌다. 알려진 예외만 구체적으로
catch하고 `except Exception`은 쓰지 않는다. 미식별 예외는 그대로 전파해 Django
Ninja/Django의 기본 500 흐름이 처리하게 한다.

application 호출이 `None`이나 명시적인 실패 Result를 반환한 경우에는 같은 controller에서
예외를 일부러 발생시킨 뒤 바로 catch하지 않는다. 준비된 ErrorOut을 즉시 반환한다.

```python
if compensation is None:
    error = CompensationFailError()
    return Status(error.status, error)
```

`detail`처럼 발생별 값이 필요한 오류는 factory를 만들지 않고 controller에서 BC base를
직접 생성한다. 이 경우에도 `code`는 자기 BC Enum 멤버를 사용한다.

```python
error = LessonErrorOut(
    code=LessonErrorCode.SCHEDULE_CONFLICT,
    title="Lesson schedule conflict",
    status=409,
    detail=f"Lesson {lesson_id} conflicts with the selected schedule.",
)
return Status(error.status, error)
```

오류 응답에 header가 필요하면 주입받은 Django `HttpResponse`에 header만 설정하고 Schema는
여전히 `Status`로 반환한다. 수제 응답 객체를 생성하지 않는다.

Django Ninja 1.6.x에서는 `(status, schema)` tuple 대신 `Status(status, schema)`를 사용한다.
수제 `Response`, `JsonResponse`, body dict는 반환하지 않는다.

### 8.3 BC controller 등록

```python
# application/lessons/lessons_api_router.py

def register_lessons_api(api: NinjaExtraAPI) -> None:
    api.register_controllers(LessonController)
```

```python
# broccoli_server/urls.py

register_accounts_api(api)
register_lessons_api(api)
```

모듈 import side effect로 controller를 등록하지 않는다. `urls.py`는 전체 BC를 아는 유일한
composition root다. `api.py`는 어떤 BC가 존재하는지 모른다. BC exception handler는 등록하지
않으며 framework custom exception handler도 등록하지 않는다.

## 9. 런타임 흐름

### 9.1 BC 에러

```text
HTTP request
-> controller가 application use case 호출
-> 알려진 domain/application 예외를 controller가 catch
-> 준비된 <Bc>ErrorOut 생성
-> controller가 Status(error.status, error) 반환
-> Ninja가 선언된 Schema로 application/json 직렬화
```

### 9.2 Framework 오류

```text
인증 함수가 None 반환 또는 AuthenticationError raise
-> Ninja 기본 401 응답

인가·route·throttle·HttpError·request validation 실패
-> Ninja/Django 기본 status와 body 반환
-> BC ErrorOut을 통과하지 않음
```

### 9.3 미식별 오류

```text
controller가 잡지 않은 raw DB/인프라/미식별 예외
-> Ninja/Django 기본 500 처리
-> custom catch-all과 custom ErrorOut 없음
```

## 10. OpenAPI 계약

1. controller는 자신이 의도적으로 반환할 수 있는 모든 BC 오류 status를 `response={...}`에
   선언한다.
2. BC 오류 status는 해당 BC의 `<Bc>ErrorOut`을 사용한다.
3. 인증·인가·route 404·검증·framework 429·미식별 500을 공통 `ErrorOut`으로 선언하지
   않는다. 인증은 OpenAPI security scheme로 표현하고 framework 기본 body는 커스텀
   Schema 계약으로 광고하지 않는다.
4. `openapi_extra`로 framework 오류 response를 수동 추가하지 않는다.
5. `get_openapi_schema` override나 별도 함수로 생성 OpenAPI를 사후 수정하지 않는다.
6. BC ErrorOut의 런타임과 OpenAPI media type은 Django Ninja 기본 `application/json`이다.
7. 같은 BC ErrorOut을 여러 status에 선언하면서 code Enum 전체가 노출되는 것은 승인된
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
| 공통 모듈 내용 | 공통 `error_out.py`에는 import와 `ErrorOut` 정의만 허용한다. Enum·concrete ErrorOut·상수·helper를 금지한다. | module body AST 검사 |
| 공통 필드 | `ErrorOut` 필드는 필수 `code/title/status/detail` 네 개뿐이다. | Schema AST 검사 |
| 금지 계약 | `type`, `about:blank`, problem URI, `retryable`, `invalid-params`, `instance`, `ValidationErrorOut`을 새 표준 에러 코드에서 사용하지 않는다. | 파일·필드·문자열·심볼 검사 |
| BC Enum 개수 | 관리 대상 오류가 있는 BC에는 `<Bc>ErrorCode(StrEnum)`가 정확히 하나다. | BC별 AST 개수·이름 검사 |
| BC base Schema | 같은 BC에는 `<Bc>ErrorOut(CommonErrorOut)` base가 정확히 하나다. | BC별 AST 개수·상속 검사 |
| BC 파일 위치 | BC Enum, base ErrorOut, 준비된 concrete ErrorOut은 `<bc>/presentation_layer/schema/error_out.py`에만 존재한다. | 정의 위치 검사 |
| BC base 형태 | `<Bc>ErrorOut`은 `code: <Bc>ErrorCode`만 재선언하고 다른 필드를 추가하지 않는다. | 클래스 필드 AST 검사 |
| concrete 형태 | 준비된 concrete ErrorOut은 `<Bc>ErrorOut`을 상속하고 공통 필드의 기본값만 고정한다. 새 필드·validator·alias는 금지한다. | 상속·필드·decorator AST 검사 |
| concrete code | 준비된 concrete ErrorOut의 `code` 기본값은 자기 BC의 `<Bc>ErrorCode` 멤버다. | annotation·기본값 AST 검사 |
| 준비 완료 | 준비된 concrete ErrorOut은 필수 인자 없이 생성할 수 있어야 한다. | 상속 필드 기본값 AST 검사 |
| 파일 증식 | `*_error_out.py`, problem별 Schema 파일, validation/retryable 전용 파일을 금지한다. | 경로 패턴 검사 |
| factory 금지 | 고정 ErrorOut 값을 채우는 `make_*`, `build_*`, `*_error()` 함수·classmethod를 만들지 않는다. | 반환 타입·이름·본문 AST 검사 |
| code 형식 | Enum 값은 소문자 snake_case다. | 정규식 검사 |
| code 고유성 | 모든 BC Enum 값은 전체 프로젝트에서 중복되지 않는다. | Enum 값 전역 집합 검사 |
| code 소비 | ErrorOut의 `code=` 또는 class 기본값에 문자열 리터럴을 직접 사용하지 않는다. 자기 BC Enum 멤버만 사용한다. | keyword·class field AST 검사 |
| 전역 계약 금지 | `GlobalErrorCode`, 전역 ErrorOut, 전역 오류 catalog를 정의하지 않는다. | 심볼·상속·mapping AST 검사 |
| 루트 격리 | `<project_config>/api.py`는 `application.*`을 import하지 않는다. | import AST 검사 |
| 루트 BC 지식 | `api.py`에는 BC 이름·BC 경로 분기·BC 예외 map이 없다. | BC 디렉터리명 기반 AST/문자열 검사 |
| 루트 오류 책임 금지 | `api.py`는 ErrorCode/ErrorOut class, 오류 catalog, 응답 helper, custom exception handler를 정의하지 않는다. | class·함수·decorator·등록 호출 AST 검사 |
| 계층 방향 | domain/application/infra는 Ninja·공통 ErrorOut·BC ErrorCode를 import하지 않는다. | 계층별 import 검사 |
| BC 격리 | 한 BC는 다른 BC의 ErrorCode/ErrorOut/예외를 import하지 않는다. | import 경로와 현재 BC 비교 |
| 응답 helper 금지 | `error_response`, `server_error_response`와 ErrorOut을 `Response`로 바꾸는 동형 helper를 금지한다. | 함수명·반환 타입·본문 AST 검사 |
| custom handler 금지 | 프로젝트 코드의 `exception_handler`, `add_exception_handler`, `error_handlers.py`를 금지한다. | 경로·decorator·등록 호출 검사 |
| controller 등록 | `<bc>_api_router.py`는 controller만 명시적인 `register_<bc>_api(api)` 안에서 등록한다. | 등록 함수·호출 AST 검사 |
| import side effect | 모듈 최상위에서 controller 등록을 실행하지 않는다. | module-level call AST 검사 |
| Validation 통과 | `ninja.errors.ValidationError` custom handler와 validation 전용 Schema를 금지한다. | import·decorator·class 검사 |
| controller 반환 | 알려진 BC 오류는 controller가 자기 BC ErrorOut을 `Status`로 반환한다. 오류용 tuple·`Response`·dict 반환은 금지한다. | return 식·호출 AST 검사 |
| controller catch | controller는 자기 BC의 구체 예외만 catch하며 `except Exception`을 두지 않는다. | `Try`/`ExceptHandler` AST 검사 |
| 즉시 재포착 금지 | controller가 같은 `try` 안에서 직접 생성한 예외를 바로 아래 `except`로 잡지 않는다. | `Raise`와 handler 타입 AST 검사 |
| OpenAPI | BC 오류 status만 `response={...}`에 BC ErrorOut으로 선언하고 framework 오류용 `openapi_extra`/사후 후가공을 쓰지 않는다. | decorator·override AST 검사 |
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
| controller 매핑 | 알려진 application/domain 예외는 그 호출을 수행하는 controller가 구체적으로 catch하고 준비된 ErrorOut을 반환한다. |
| 반복 허용 | 서로 다른 controller에 몇 줄의 명시적인 예외→ErrorOut 변환이 반복되어도 성급한 handler·factory 공통화를 하지 않는다. |
| try 범위 | 예외 계약을 가진 application 호출만 감싸며 출력 변환이나 무관한 로직까지 넓히지 않는다. |
| 실패 Result | `None`이나 실패 Result는 같은 controller에서 예외로 만들었다가 바로 잡지 않고 ErrorOut을 직접 반환한다. |
| 알 수 없는 BC 예외 | controller에서 잡지 않고 Ninja/Django 기본 500 흐름까지 전파한다. |
| framework 오류 | 401/403/route 404/422/429/일반 HttpError/미식별 500은 custom ErrorOut으로 바꾸지 않는다. |
| 인증 실패 | 인증 함수는 ErrorOut을 반환하지 않고 `None` 반환 또는 `AuthenticationError` raise로 Ninja 기본 401을 사용한다. |
| raw 인프라 오류 | 전역 status를 추측하지 않는다. 공개할 의미가 있으면 BC 예외로 정규화해 controller가 처리한다. |
| 운영 500 보호 | framework 기본 500을 쓰는 운영 환경은 `DEBUG=False`를 유지한다. custom catch-all로 대체하지 않는다. |
| 확장 필드 | 현재 표준에서는 추가하지 않는다. 실제 요구가 생기면 별도 계약 변경으로 심사한다. |
| api.py 책임 | API 인스턴스와 API 자체 설정만 둔다. 에러 타입·catalog·helper·custom handler를 넣지 않는다. |
| brownfield | 이미 확립된 외부 에러 계약은 자동으로 깨지 않는다. 변경은 호환성 결정을 승인받는다. |
| 클라이언트 | code를 문자열 상수로 흩뿌리지 않고 생성·수기 Enum 한 곳에서 소비한다. |

## 13. 백스탑 소유와 변경 방향

기존 checker를 다음처럼 강화한다. 같은 판단을 여러 스크립트에 중복하지 않는다.

| checker | 최종 책임 |
|---|---|
| `check-error-centralization.py` | 공통 파일 집합·4필드 ErrorOut shape·BC Enum/base/concrete Schema 위치와 형태·code 형식/중복/Enum 소비·전역 계약/factory/validation 금지 |
| `check-context-isolation.py` | root API의 BC 의존·계층별 Ninja 의존·BC 간 에러 계약 import 금지 |
| `check-openapi-error-declaration.py` | controller가 직접 반환하는 BC 오류의 `response=` 선언과 framework 오류용 `openapi_extra`·후가공 금지 |
| `check-catch-all-handler.py` | 기존 catch-all 존재 강제가 새 계약과 반대이므로 제거한다. custom handler 금지는 아래 checker로 이동한다. |
| 신규 `check-api-error-controller-contract.py` | custom handler/응답 helper 금지·controller의 `Status` 오류 반환·구체 catch·즉시 재포착 금지·명시적 controller registrar·module import side effect 금지 |

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
- 준비된 concrete ErrorOut은 인자 없이 생성되고 승인된 code/title/status/detail을 가진다.
- concrete ErrorOut은 base에 없는 필드를 추가하지 않는다.
- BC code 값이 전체 프로젝트에서 중복되지 않는다.

### 14.2 BC mapping 테스트

각 공개 code에 대해 최소한 다음을 고정한다.

- 입력 예외 타입
- 출력 code
- HTTP/body status
- 안정적인 title
- 민감정보가 없는 detail
- 필요한 HTTP header

각 공개 BC 오류는 controller의 application 협력자를 해당 예외로 실패시키고 실제 HTTP
응답을 확인한다. 별도 mapping 함수가 없으므로 함수 단위 mapping 테스트를 만들지 않는다.
준비된 ErrorOut의 고정값은 Schema 단위 테스트가 담당하고, controller 테스트는 예외 선택과
HTTP 직렬화를 담당한다. 미식별 예외는 BC ErrorOut으로 바뀌지 않고 framework 기본 500
흐름으로 가는지도 대표 사례로 확인한다.

### 14.3 Framework 기본 처리 smoke test

- 인증 실패가 Ninja 기본 401을 반환한다.
- 인가 실패가 Ninja 기본 403을 반환한다.
- route 404, throttling 429, 미식별 예외가 framework 기본 흐름을 따른다.
- framework 오류 body가 BC ErrorOut shape나 BC code로 변환되지 않는다.
- framework 기본 body 전체를 snapshot으로 고정하지 않는다.

### 14.4 요청 검증 회귀 테스트

잘못된 요청이 Ninja 기본 422로 반환되고 커스텀 `ErrorOut`으로 변환되지 않는지만 확인한다.
Pydantic/Ninja의 내부 body 전체를 snapshot으로 고정하지 않는다.

### 14.5 OpenAPI 계약 테스트

- controller가 선언한 각 관리 대상 status가 생성 OpenAPI에 존재한다.
- BC 오류 status는 해당 `<Bc>ErrorOut`을 참조한다.
- framework 기본 오류 status를 공통 `ErrorOut`으로 광고하지 않는다.
- 수동 `openapi_extra`나 사후 후가공 없이 생성된다.
- BC ErrorOut의 런타임과 문서 media type이 `application/json`이다.

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
| `instance` | 제거 |
| 에러별/전역 problem catalog | BC별 ErrorCode Enum과 준비된 BC ErrorOut |
| 커스텀 framework 오류 | Django Ninja/Django 기본 오류 응답 |

서버와 인하우스 클라이언트를 같은 계약 버전으로 함께 배포한다. `type`과 `code`를 동시에
내보내는 장기 호환 계층은 만들지 않는다. 기존 클라이언트가 동시에 남아 있어야 한다면
이 설계를 바로 구현하지 않고 API version 분리 또는 짧은 전환 기간을 별도 승인받는다.

### 15.2 Broccoli 서버 정리 대상

1. `common/ninja/response/error_out.py`를 `code/title/status/detail` 네 필드 shape로 교체한다.
2. `common/ninja/response/validation_error_out.py`를 삭제한다.
3. `GlobalErrorCode`, 전역 ErrorOut/catalog, `error_response()`, `server_error_response()`를 만들지 않는다.
4. `problem_response`, `problem`, `problem_from_slug`, `_slug`, `PROBLEM_BASE`를 제거한다.
5. `_DOMAIN_PROBLEMS`, `_PROBLEM_DETAILS`, `_EXCEPTION_PROBLEM_DETAILS`를 제거한다.
6. `broccoli_server/api.py`의 모든 `application.*` import와 custom exception handler를 제거한다.
7. 각 HTTP BC에 단일 `<Bc>ErrorCode`, `<Bc>ErrorOut` base와 필요한 준비된 concrete ErrorOut을 같은 `error_out.py`에 만든다.
8. 각 controller가 자기 application/domain 예외를 catch해 `Status(error.status, error)`로 직접 반환하게 한다.
9. 각 BC router를 controller만 등록하는 명시적 `register_<bc>_api(api)` 함수로 바꾼다.
10. `urls.py`가 모든 BC registrar를 명시적으로 호출한다.
11. Managed Copy 같은 BC path-specific response policy를 해당 BC presentation으로 이동한다.
12. framework 오류용 OpenAPI 선언·수동 augmentation을 제거하고 BC 오류만 controller `response=`에 선언한다.
13. 서버와 클라이언트의 code Enum 및 계약 테스트를 함께 갱신한다.

현재 Broccoli 작업 트리에는 사용자 소유의 대규모 변경과 삭제가 있으므로 구현 시 이를
원복하거나 함께 커밋하지 않는다. 에러 마이그레이션은 그 변경 위에서 별도 diff로 식별
가능해야 한다.

### 15.3 dddjango 플러그인 정본 변경 범위

이 명세 승인 후 구현 계획은 최소한 다음 정본을 다룬다.

- `dddjango/skills/architecture-api/references/final.md`
- `dddjango/skills/implementation-django-ninja/references/final.md`
- `dddjango/skills/discipline-houserules/references/final.md`
- 해당 `SKILL.md` 핵심 운영 원칙
- operation의 오류 `raise`·중앙 BC handler 강제를 controller 직접 `Status` 반환 규칙으로 교체
- `GlobalErrorCode`·전역 ErrorOut·응답 helper·custom catch-all 강제를 제거하고 framework 기본 처리로 교체
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
- framework 기본 오류를 공통 ErrorOut으로 통일하는 것
- 전역 오류 code·catalog·handler·응답 helper를 만드는 것
- 에러별 파일·handler·고정값 factory를 만드는 것
- 임의 확장 필드와 범용 extension bag을 지원하는 것
- 기존 RFC 9457 brownfield API를 승인 없이 자동 이주하는 것
- 줄 수만으로 `api.py`를 합격·실패시키는 것

## 17. 승인 기준

다음 문장이 모두 참이면 이 설계를 승인한다.

1. 새 dddjango 표준은 RFC 9457 URI `type`이 아니라 문자열 `code`를 사용한다.
2. controller가 의도적으로 반환하는 BC ErrorOut은 모두 `code/title/status/detail`을 포함한다.
3. 인증·인가·route 404·요청 검증·throttling·raw 인프라·미식별 오류는 이 커스텀 계약 밖에 두고 framework 기본 처리를 사용한다.
4. 공통 response 디렉터리에는 `error_out.py` 한 production module만 둔다.
5. 공통 `ErrorOut`은 네 필드 wire shape만 알고 BC code를 모른다.
6. 각 BC는 ErrorCode Enum 하나와 ErrorOut base 하나를 소유한다.
7. 준비된 concrete ErrorOut은 같은 BC `error_out.py`에서 공통 필드 기본값만 고정하고 인자 없이 생성된다.
8. BC 에러별 `Literal`, 별도 Schema 파일, factory, exception handler를 만들지 않는다.
9. `GlobalErrorCode`, 전역 ErrorOut/catalog, 응답 helper, custom exception handler와 catch-all을 만들지 않는다.
10. 알려진 BC 예외는 해당 controller가 catch하고 준비된 ErrorOut을 `Status`로 직접 반환한다.
11. `api.py`에는 에러 타입·catalog·helper·custom handler와 BC import·mapping·path 분기가 없다.
12. 미식별 예외는 controller가 잡지 않고 Ninja/Django 기본 500 흐름이 처리한다.
13. BC 오류의 `response=`와 생성 OpenAPI가 실제 BC Schema 계약을 광고한다.
14. framework 기본 오류를 공통 ErrorOut으로 거짓 광고하지 않는다.
15. 구조 불변식은 touched-file이 아니라 전체 트리 백스탑으로 검사한다.
16. 서버와 인하우스 클라이언트는 breaking contract를 함께 전환한다.

## 18. 대체 관계

이 문서가 사용자 승인을 받으면 2026-07-16 `ErrorOut` 중앙 계약 설계의 다음 결정을
대체한다.

- RFC 9457 `type`/`about:blank` core profile
- `application/problem+json` runtime 계약
- validation 전용 공통 concrete Schema
- 서로 다른 wire shape·확장 필드를 가진 problem-specific concrete ErrorOut 증식 허용
- `retryable`/extension 중심 표현
- BC problem type URI 매핑

유지되는 핵심은 공통 `ErrorOut`의 단일 소유, domain/application의 HTTP 무지, BC 오류의
명시적인 OpenAPI response 선언이다. BC 오류 흐름은 raise-only+중앙 handler가 아니라
controller의 구체 catch+준비된 ErrorOut 직접 반환으로 대체하고, framework 오류는 별도
전역 계약 없이 Django Ninja/Django 기본 처리에 맡긴다.
