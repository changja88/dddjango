from django.http import JsonResponse


def problem_response(
    *,
    status: int,
    type_: str,
    title: str,
    detail: str,
    **extensions: object,
) -> JsonResponse:
    body = {
        "type": type_,
        "title": title,
        "status": status,
        "detail": detail,
    }
    body.update(extensions)
    return JsonResponse(body, status=status, content_type="application/problem+json")
