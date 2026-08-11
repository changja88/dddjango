from django.db import OperationalError
from ninja import NinjaAPI

api = NinjaAPI()


@api.exception_handler(OperationalError)
def handle_operational(request, exc: OperationalError):
    if "deadlock" in str(exc) or "lock" in str(exc):
        return api.create_response(request, {"detail": "retry"}, status=503)
    return api.create_response(request, {"detail": "internal"}, status=500)
