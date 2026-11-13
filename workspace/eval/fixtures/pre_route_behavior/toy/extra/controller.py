from typing import Optional
from uuid import UUID

from ninja import File, Form, Query, Router, Schema
from ninja.files import UploadedFile
from ninja.security import HttpBearer, django_auth
from ninja.throttling import AnonRateThrottle


class TokenAuth(HttpBearer):
    def authenticate(self, request, token):
        return "user" if token == "good" else None


def plain_auth(request):
    return "u" if request.headers.get("X-Key") == "k" else None


class FilterIn(Schema):
    q: Optional[str] = None
    tag: Optional[str] = None


class FormIn(Schema):
    name: str


class ItemIn(Schema):
    title: str


router = Router()


@router.get("/plain-auth", auth=plain_auth, response={200: dict})
def plain_auth_route(request):
    return {"ok": True}


@router.get("/int-conv/{int:item_id}", response={200: dict})
def int_conv(request, item_id: int):
    return {"id": item_id}


@router.get("/uuid-conv/{uuid:item_id}", response={200: dict})
def uuid_conv(request, item_id: UUID):
    return {"id": str(item_id)}


@router.get("/uuid-plain/{item_id}", response={200: dict})
def uuid_plain(request, item_id: UUID):
    return {"id": str(item_id)}


@router.get("/opt-str", response={200: dict})
def opt_str(request, q: Optional[str] = None):
    return {"q": q}


@router.get("/filter", response={200: dict})
def filter_route(request, filters: Query[FilterIn]):
    return filters.dict()


@router.get("/list-str", response={200: dict})
def list_str(request, tags: list[str] = Query(None)):
    return {"tags": tags}


@router.post("/form", response={200: dict})
def form_route(request, data: Form[FormIn]):
    return {"name": data.name}


@router.post("/upload", response={200: dict})
def upload(request, file: File[UploadedFile]):
    return {"size": file.size}


@router.post("/session", auth=django_auth, response={200: dict})
def session_route(request):
    return {"ok": True}


@router.post("/throttled", throttle=AnonRateThrottle("1/m"), response={200: dict})
def throttled(request):
    return {"ok": True}


@router.post("/item", response={200: dict})
def item(request, body: ItemIn):
    return {"t": body.title}


class TooManyAttemptsError(Schema):
    error: str


@router.post(
    "/attempt",
    throttle=AnonRateThrottle("100/m"),
    response={200: dict, 429: TooManyAttemptsError},
    openapi_extra={"responses": {429: {"headers": {"Retry-After": {"required": True, "description": "다시 시도까지 초",
                                                                  "schema": {"type": "integer"}}}}}},
)
def attempt(request):
    return {"ok": True}


secured = Router(auth=TokenAuth())


@secured.get("/router-auth", response={200: dict})
def router_auth(request):
    return {"ok": True}
