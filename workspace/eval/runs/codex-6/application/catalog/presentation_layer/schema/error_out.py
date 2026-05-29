from typing import Optional

from django.http import JsonResponse


def problem_response(
    *,
    status: int,
    problem_type: str,
    title: str,
    detail: str,
    extensions: Optional[dict[str, object]] = None,
) -> JsonResponse:
    body: dict[str, object] = {
        "type": problem_type,
        "title": title,
        "status": status,
        "detail": detail,
    }
    if extensions:
        body.update(extensions)

    return JsonResponse(body, status=status, content_type="application/problem+json")
