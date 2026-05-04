현재 작업 디렉터리는 읽기 전용이고 `config.toml`/`AGENTS.md`도 발견되지 않아 파일 반영은 못 했습니다. 아래는 그대로 팀 컨벤션 문서에 넣을 수 있는 형태입니다.

**Django Ninja Pagination / Error Response Standard**

### 1. Pagination 규칙

1. 모든 컬렉션 `GET` 엔드포인트는 반드시 페이지네이션을 적용한다. 예외는 enum, 설정값, 20개 이하로 고정된 정적 목록뿐이다.
2. 공개 API와 변경이 잦은 목록은 `CursorPagination`을 기본으로 사용한다.
3. 관리자 화면, 내부 백오피스, 랜덤 페이지 접근이 필요한 소규모 목록만 `LimitOffsetPagination`을 허용한다.
4. 기본 페이지 크기는 `50`, 최대 페이지 크기는 `100`으로 제한한다.
5. Cursor 기반 목록은 반드시 안정적인 정렬을 가진다. 기본 정렬은 `("-created_at", "-id")`처럼 유니크한 tie-breaker를 포함한다.
6. 페이지네이션 정렬 필드에는 DB 인덱스를 둔다. 대량 테이블에서 인덱스 없는 정렬은 금지한다.
7. 클라이언트가 전달하는 `ordering`은 allowlist 기반으로만 허용한다.
8. 페이지네이션되지 않은 `list[Schema]` 응답은 코드 리뷰에서 차단한다.

```python
# common/api/pagination.py
from collections.abc import Callable
from typing import Any

from ninja.pagination import CursorPagination, LimitOffsetPagination, paginate

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100
DEFAULT_CURSOR_ORDERING = ("-created_at", "-id")


def cursor_paginate(
    *,
    ordering: tuple[str, ...] = DEFAULT_CURSOR_ORDERING,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> Callable[..., Any]:
    return paginate(
        CursorPagination,
        ordering=ordering,
        page_size=page_size,
        max_page_size=MAX_PAGE_SIZE,
    )


def limit_offset_paginate() -> Callable[..., Any]:
    return paginate(LimitOffsetPagination)
```

```python
# settings.py
NINJA_PAGINATION_PER_PAGE = 50
NINJA_PAGINATION_MAX_OFFSET = 10_000
```

```python
# projects/api.py
from django.db.models import QuerySet
from ninja import Router

from common.api.pagination import cursor_paginate
from projects.models import Project
from projects.schemas import ProjectOut

router = Router(tags=["projects"])


@router.get("", response=list[ProjectOut])
@cursor_paginate(ordering=("-created_at", "-id"))
def list_projects(request) -> QuerySet[Project]:
    return (
        Project.objects.visible_to(request.user)
        .order_by("-created_at", "-id")
    )
```

Cursor 응답은 Django Ninja 기본 형식을 사용한다.

```json
{
  "next": "https://api.example.com/v1/projects?cursor=...",
  "previous": null,
  "results": [
    {"id": "prj_123", "name": "Website Renewal"}
  ]
}
```

### 2. Error Response 규칙

1. 모든 API 에러는 RFC 9457 Problem Details 형식을 사용한다.
2. 에러 응답 `Content-Type`은 `application/problem+json`이다.
3. 필수 필드는 `type`, `title`, `status`, `detail`, `instance`다.
4. `type`은 안정적인 URI로 관리한다. 예: `https://api.example.com/problems/validation-failed`
5. `title`은 에러 유형별로 고정한다. 요청마다 달라지는 설명은 `detail`에 넣는다.
6. `message`, `error`, `errors`만 단독으로 반환하는 커스텀 형식은 금지한다.
7. 검증 오류는 `422`로 반환하고, 필드별 오류는 확장 필드 `errors`에 담는다.
8. 인증 실패는 `401`, 권한 부족은 `403`, 중복/상태 충돌은 `409`, rate limit은 `429`를 사용한다.
9. `5xx` 응답에는 내부 예외 메시지, SQL, traceback, secret을 노출하지 않는다.
10. 엔드포인트의 OpenAPI `response`에는 성공 스키마와 `ProblemDetail`을 함께 선언한다.

```python
# common/api/errors.py
from dataclasses import dataclass, field
from typing import Any

from django.http import Http404, JsonResponse
from ninja import NinjaAPI, Schema
from ninja.errors import (
    AuthenticationError,
    AuthorizationError,
    HttpError,
    ValidationError,
)


PROBLEM_BASE_URL = "https://api.example.com/problems/"


class ProblemDetail(Schema):
    type: str
    title: str
    status: int
    detail: str
    instance: str
    code: str | None = None
    errors: list[dict[str, Any]] | None = None


@dataclass(slots=True)
class APIProblem(Exception):
    status: int
    code: str
    title: str
    detail: str
    extra: dict[str, Any] = field(default_factory=dict)


def problem_response(
    request,
    *,
    status: int,
    code: str,
    title: str,
    detail: str,
    extra: dict[str, Any] | None = None,
) -> JsonResponse:
    body = {
        "type": f"{PROBLEM_BASE_URL}{code}",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": request.path,
        "code": code,
    }
    if extra:
        body.update(extra)

    return JsonResponse(
        body,
        status=status,
        content_type="application/problem+json",
    )


def install_problem_handlers(api: NinjaAPI) -> None:
    @api.exception_handler(APIProblem)
    def handle_api_problem(request, exc: APIProblem):
        return problem_response(
            request,
            status=exc.status,
            code=exc.code,
            title=exc.title,
            detail=exc.detail,
            extra=exc.extra,
        )

    @api.exception_handler(ValidationError)
    def handle_validation_error(request, exc: ValidationError):
        return problem_response(
            request,
            status=422,
            code="validation-failed",
            title="Validation Failed",
            detail="Request validation failed.",
            extra={"errors": getattr(exc, "errors", [])},
        )

    @api.exception_handler(AuthenticationError)
    def handle_authentication_error(request, exc: AuthenticationError):
        return problem_response(
            request,
            status=401,
            code="authentication-required",
            title="Authentication Required",
            detail="Valid authentication credentials are required.",
        )

    @api.exception_handler(AuthorizationError)
    def handle_authorization_error(request, exc: AuthorizationError):
        return problem_response(
            request,
            status=403,
            code="permission-denied",
            title="Permission Denied",
            detail="You do not have permission to access this resource.",
        )

    @api.exception_handler(Http404)
    def handle_not_found(request, exc: Http404):
        return problem_response(
            request,
            status=404,
            code="not-found",
            title="Not Found",
            detail="The requested resource was not found.",
        )

    @api.exception_handler(HttpError)
    def handle_http_error(request, exc: HttpError):
        status = getattr(exc, "status_code", 500)
        return problem_response(
            request,
            status=status,
            code="http-error",
            title="HTTP Error",
            detail=str(exc),
        )

    @api.exception_handler(Exception)
    def handle_unexpected_error(request, exc: Exception):
        return problem_response(
            request,
            status=500,
            code="internal-server-error",
            title="Internal Server Error",
            detail="An unexpected error occurred.",
        )
```

```python
# api.py
from ninja import NinjaAPI

from common.api.errors import install_problem_handlers

api = NinjaAPI(title="Service API", version="1.0.0")
install_problem_handlers(api)
```

```python
# projects/api.py
from ninja.responses import codes_4xx, codes_5xx

from common.api.errors import APIProblem, ProblemDetail


@router.post(
    "",
    response={201: ProjectOut, codes_4xx: ProblemDetail, codes_5xx: ProblemDetail},
)
def create_project(request, payload: ProjectCreateIn):
    if Project.objects.filter(slug=payload.slug).exists():
        raise APIProblem(
            status=409,
            code="project-slug-conflict",
            title="Project Slug Conflict",
            detail="A project with this slug already exists.",
        )

    project = Project.objects.create(**payload.dict())
    return 201, project
```

---
> **관련 스킬 참조:**
> - API 상태 코드, RFC 9457, 페이지네이션 전략 → **architecture-api** 스킬
> - Django Ninja `Schema`, `Router`, `@paginate`, 예외 핸들러 구현 → **implementation-django-ninja** 스킬