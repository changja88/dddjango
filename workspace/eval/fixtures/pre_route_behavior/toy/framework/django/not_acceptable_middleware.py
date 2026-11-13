from django.http import JsonResponse

CSV_ONLY_PATHS = ("/api3/pub/list",)


class NotAcceptableMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path in CSV_ONLY_PATHS and request.headers.get("Accept") == "text/csv":
            return JsonResponse({"error": "not_acceptable"}, status=406)
        return self.get_response(request)
