import re

from django.conf import settings
from django.http import JsonResponse


class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.MAINTENANCE_MODE and request.path.startswith("/api/") and not self._exempted(request.path):
            response = JsonResponse({"error": "service_maintenance", "message": "The service is under maintenance."}, status=503)
            response["Service-Maintenance-Ends-At"] = "2026-11-13T03:00:00Z"
            return response
        return self.get_response(request)

    def _exempted(self, path):
        return path in settings.MAINTENANCE_MODE_EXEMPT_PATHS or any(
            re.fullmatch(pattern, path) for pattern in settings.MAINTENANCE_MODE_EXEMPT_PATTERNS
        )
