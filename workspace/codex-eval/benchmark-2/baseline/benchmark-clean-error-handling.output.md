현재 `/private/tmp/dddjango-codex-eval`에는 `config.toml`이나 프로젝트 파일이 없어 실제 파일에는 반영할 수 없었습니다. 대신 Django Ninja 기준으로 바로 적용 가능한 표준안을 정리합니다.

**표준 원칙**

Domain exception은 HTTP를 몰라야 합니다.

즉, 도메인 계층에서는 `404`, `400`, `Response`, `NinjaAPI` 같은 API 개념을 절대 사용하지 않습니다. 도메인은 “무엇이 잘못됐는가”만 표현하고, API 계층이 이를 HTTP status와 response body로 변환합니다.

```text
domain/service
  raises DomainException

application/usecase
  may catch/rethrow or enrich DomainException

api/presentation
  maps DomainException -> HTTP error response
```

**Domain Exception 표준**

도메인 예외는 최소한 아래 정보를 가집니다.

```python
# domain/exceptions.py

from dataclasses import dataclass
from typing import Any


@dataclass(eq=False)
class DomainException(Exception):
    code: str
    message: str
    detail: dict[str, Any] | None = None


class EntityNotFound(DomainException):
    def __init__(self, entity: str, entity_id: str | int):
        super().__init__(
            code=f"{entity.upper()}_NOT_FOUND",
            message=f"{entity} not found",
            detail={"entity": entity, "id": entity_id},
        )


class BusinessRuleViolation(DomainException):
    def __init__(self, code: str, message: str, detail: dict[str, Any] | None = None):
        super().__init__(code=code, message=message, detail=detail)
```

권장 규칙:

- `code`: 클라이언트와 로그에서 추적 가능한 안정적인 식별자
- `message`: 사용자 또는 클라이언트 개발자가 이해할 수 있는 짧은 설명
- `detail`: 디버깅 가능한 구조화 데이터
- HTTP status는 넣지 않음
- Django/Ninja 객체를 import하지 않음

**API Error Response 표준**

API 응답은 일관된 envelope을 사용합니다.

```python
# api/schemas.py

from ninja import Schema
from typing import Any


class ErrorResponse(Schema):
    code: str
    message: str
    detail: dict[str, Any] | None = None
```

예시 응답:

```json
{
  "code": "USER_NOT_FOUND",
  "message": "User not found",
  "detail": {
    "entity": "user",
    "id": 123
  }
}
```

**Exception Mapping 표준**

도메인 예외와 HTTP status의 연결은 API 계층에서만 관리합니다.

```python
# api/errors.py

from http import HTTPStatus
from ninja import NinjaAPI
from django.http import HttpRequest

from domain.exceptions import (
    DomainException,
    EntityNotFound,
    BusinessRuleViolation,
)


DOMAIN_EXCEPTION_STATUS_MAP: dict[type[DomainException], int] = {
    EntityNotFound: HTTPStatus.NOT_FOUND,
    BusinessRuleViolation: HTTPStatus.BAD_REQUEST,
}


def status_for_exception(exc: DomainException) -> int:
    for exc_type, status in DOMAIN_EXCEPTION_STATUS_MAP.items():
        if isinstance(exc, exc_type):
            return int(status)

    return int(HTTPStatus.BAD_REQUEST)


def register_exception_handlers(api: NinjaAPI) -> None:
    @api.exception_handler(DomainException)
    def handle_domain_exception(request: HttpRequest, exc: DomainException):
        return api.create_response(
            request,
            {
                "code": exc.code,
                "message": exc.message,
                "detail": exc.detail,
            },
            status=status_for_exception(exc),
        )
```

그리고 API 생성부에서 한 번만 등록합니다.

```python
# api/main.py

from ninja import NinjaAPI
from api.errors import register_exception_handlers

api = NinjaAPI()
register_exception_handlers(api)
```

**상태 코드 기준**

권장 매핑은 다음처럼 고정합니다.

```text
EntityNotFound              -> 404
AlreadyExists / Duplicated  -> 409
BusinessRuleViolation       -> 400
PermissionDenied            -> 403
AuthenticationRequired      -> 401
InvalidStateTransition      -> 409
ExternalServiceFailure      -> 502
RateLimitExceeded           -> 429
```

중요한 기준은 “예외 이름으로 HTTP status를 유추할 수 있어야 한다”입니다.  
예를 들어 `BusinessRuleViolation`은 너무 넓으므로, 상태별 처리가 많아지면 `InvalidStateTransition`, `QuotaExceeded`, `AlreadyExists`처럼 더 구체적인 예외로 분리합니다.

**사용 예시**

도메인 서비스:

```python
# domain/user_service.py

from domain.exceptions import EntityNotFound, BusinessRuleViolation


def activate_user(user):
    if user is None:
        raise EntityNotFound("user", "unknown")

    if user.is_blocked:
        raise BusinessRuleViolation(
            code="BLOCKED_USER_CANNOT_BE_ACTIVATED",
            message="Blocked user cannot be activated",
            detail={"user_id": user.id},
        )

    user.activate()
```

API 라우터:

```python
# api/users.py

from ninja import Router

router = Router()


@router.post("/{user_id}/activate")
def activate_user(request, user_id: int):
    user = get_user(user_id)
    activate_user_service(user)

    return {"ok": True}
```

라우터에서는 `try/except DomainException`을 반복하지 않습니다.  
공통 exception handler가 변환 책임을 가집니다.

**클린 코드 기준**

이 프로젝트의 표준은 이렇게 잡는 것이 좋습니다.

1. 도메인 예외는 HTTP를 모른다.
2. API 계층만 HTTP status를 결정한다.
3. 에러 응답 schema는 전 API에서 하나로 통일한다.
4. 라우터마다 `try/except`를 쓰지 않는다.
5. 예외는 문자열 비교가 아니라 타입으로 분기한다.
6. `code`는 클라이언트 계약이므로 쉽게 바꾸지 않는다.
7. 예상 가능한 비즈니스 실패는 `DomainException`, 예상 못 한 버그는 500으로 둔다.
8. 로그에는 `code`, `detail`, request id를 남긴다.
9. validation error와 domain error의 response shape도 가능하면 맞춘다.

**추천 디렉터리 구조**

```text
app/
  domain/
    exceptions.py
    user_service.py

  api/
    main.py
    errors.py
    schemas.py
    users.py
```

핵심은 “도메인은 의미 있는 실패를 던지고, API는 그것을 프로토콜에 맞게 번역한다”입니다.  
이 기준을 지키면 도메인 로직은 테스트하기 쉬워지고, API 응답은 클라이언트 입장에서 예측 가능해집니다.