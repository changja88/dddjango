from django.conf import settings
from django.http import JsonResponse

UNSAFE = {"POST", "PUT", "PATCH", "DELETE"}


class CrossSiteRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in UNSAFE and request.headers.get("Sec-Fetch-Site") == "cross-site" and not (request.method == "POST" and request.path in settings.CROSS_SITE_REQUEST_EXEMPT_PATHS):
            return JsonResponse({"error": "cross_site_request", "message": "Cross-site request rejected."}, status=403)
        return self.get_response(request)
