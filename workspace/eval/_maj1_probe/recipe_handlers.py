# §6.2 레시피 핸들러 추출(final.md:364-504) — AST 파싱용 코퍼스. 실행 아님.
import logging
from http import HTTPStatus

from django.db import IntegrityError, OperationalError
from ninja import NinjaAPI
from ninja.errors import HttpError, ValidationError
from ninja.responses import Response

logger = logging.getLogger(__name__)
api = NinjaAPI()


def problem(status, *, title, detail, type="about:blank", **ext):
    body = {"type": type, "title": title, "status": status, "detail": detail, **ext}
    return Response(body, status=status, content_type="application/problem+json")


@api.exception_handler(ProductNotFound)
def on_product_not_found(request, exc):
    return problem(404, title="Product not found", detail=str(exc))


@api.exception_handler(InsufficientStock)
def on_insufficient_stock(request, exc):
    return problem(409, title="Insufficient stock", detail=str(exc))


@api.exception_handler(ValidationError)
def on_validation_error(request, exc):
    return problem(422, title="Validation failed", detail="Request did not pass validation.",
                   **{"invalid-params": exc.errors})


@api.exception_handler(HttpError)
def on_http_error(request, exc):
    try:
        title = HTTPStatus(exc.status_code).phrase
    except ValueError:
        title = "Request error"
    return problem(exc.status_code, type="about:blank", title=title, detail=str(exc))


def _server_error(request, exc):
    logger.exception("Unhandled exception at API boundary")
    return problem(500, type="about:blank", title="Internal server error",
                   detail="An unexpected error occurred.")


def _is_retryable_db_error(exc):
    msg = str(exc).lower()
    if "locked" in msg or "deadlock detected" in msg or "could not serialize access" in msg:
        return True
    cause = exc.__cause__
    code = getattr(cause, "sqlstate", None) or getattr(cause, "pgcode", None)
    return code in {"40001", "40P01"}


@api.exception_handler(OperationalError)       # C: 분기 有 → 면제 기대
def on_db_operational_error(request, exc):
    if not _is_retryable_db_error(exc):
        return _server_error(request, exc)
    resp = problem(503, type="about:blank", title="Service temporarily unavailable",
                   detail="Transient database contention; please retry.")
    resp["Retry-After"] = "1"
    return resp


@api.exception_handler(IntegrityError)         # B: IntegrityError 500 → 비대상 기대
def on_integrity_error(request, exc):
    return _server_error(request, exc)


@api.exception_handler(Exception)
def on_unhandled(request, exc):
    return _server_error(request, exc)


# 대안 B(create_response 오버라이드) — 핸들러 0개·전수 변환 → 대상 0 기대
class ProblemAPI(NinjaAPI):
    def create_response(self, request, data, *, status=200, **kwargs):
        response = super().create_response(request, data, status=status, **kwargs)
        if status >= 400:
            response["content-type"] = "application/problem+json"
        return response
