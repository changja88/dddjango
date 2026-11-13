"""경로 앞 응답 표 — 프로젝트 미들웨어 · 앞단이 보내는 답."""
from ninja import Schema


class CrossSiteRequestRejectedOut(Schema):
    error: str
    message: str


class ServiceMaintenanceOut(Schema):
    error: str
    message: str


class NotAcceptableOut(Schema):
    error: str


PRE_ROUTE_RESPONSES: tuple[dict[str, object], ...] = (
    {
        "status": 403,
        "when": "all",
        "methods": ("POST", "PUT", "PATCH", "DELETE"),
        "exempt": ("POST", "CROSS_SITE_REQUEST_EXEMPT_PATHS"),
        "description": "다른 사이트에서 온 요청 거절",
        "body": CrossSiteRequestRejectedOut,
    },
    {
        "status": 503,
        "when": "all",
        "namespaces": ("api",),
        "exempt": (None, "MAINTENANCE_MODE_EXEMPT_PATHS"),
        "description": "점검 중",
        "body": ServiceMaintenanceOut,
        "headers": {"Service-Maintenance-Ends-At": {"schema": {"type": "string", "format": "date-time"}}},
    },
    {"status": 413, "when": "body", "description": "앞단이 받는 크기를 넘음", "media_type": "text/html"},
    {
        "status": 406,
        "when": "all",
        "namespaces": ("api3",),
        "operations": ("pub_list",),
        "description": "받을 수 없는 형식",
        "body": NotAcceptableOut,
    },
)

NOT_API_MIDDLEWARE: tuple[str, ...] = ()

BAD_REQUEST_RESPONSE: dict[str, object] = {"media_type": "text/html"}
