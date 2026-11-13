from django.conf import settings
from django.http import JsonResponse


class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.MAINTENANCE_MODE and request.path.startswith("/api/") and request.path not in settings.MAINTENANCE_MODE_EXEMPT_PATHS:
            response = JsonResponse({"error": "service_maintenance", "message": "The service is under maintenance."}, status=503)
            response["Service-Maintenance-Ends-At"] = "2026-11-13T03:00:00Z"
            return response
        return self.get_response(request)
