from django.db import OperationalError
from ninja import NinjaAPI

api = NinjaAPI()


@api.exception_handler(OperationalError)
def handle_operational(request, exc: OperationalError):
    return api.create_response(request, {"detail": "retry later"}, status=503)
