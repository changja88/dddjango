from django.http import HttpRequest, JsonResponse

from toyproj.urls import urlpatterns  # noqa: F401 — 같은 경로 · Django 400 처리기만 JSON


def bad_request_json(request: HttpRequest, exception: Exception | None = None) -> JsonResponse:
    return JsonResponse({"error": "bad_request"}, status=400)


handler400 = "toyproj.urls_json400.bad_request_json"
