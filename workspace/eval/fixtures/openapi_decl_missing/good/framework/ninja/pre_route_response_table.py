"""경로 앞 응답 표 — 프로젝트 미들웨어 · 앞단이 보내는 답(설계 G1 승인)."""
from ninja import Schema


class ServiceMaintenanceOut(Schema):
    error: str
    message: str


PRE_ROUTE_RESPONSES: tuple[dict[str, object], ...] = (
    {
        "status": 503,
        "when": "all",
        "namespaces": ("api",),
        "description": "점검 중",
        "body": ServiceMaintenanceOut,
        "headers": {"Service-Maintenance-Ends-At": {"schema": {"type": "string", "format": "date-time"}}},
    },
    {"status": 413, "when": "body", "description": "앞단이 받는 크기를 넘음", "media_type": "text/html"},
)

NOT_API_MIDDLEWARE: tuple[str, ...] = ()

BAD_REQUEST_RESPONSE: dict[str, object] = {"media_type": "text/html"}
