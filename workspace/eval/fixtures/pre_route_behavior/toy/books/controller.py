from collections.abc import Mapping, Sequence

from django.http import HttpResponse
from ninja import Router, Schema, Status
from ninja.security import HttpBearer


class TokenAuth(HttpBearer):
    def authenticate(self, request, token):
        return "user" if token == "good" else None


# 프로젝트 자기 `JsonValue` 별칭(implementation-python 규범 꼴) — 생성 문서에 같은 이름 component 가 선다.
# 정본이 이 이름으로 다른 꼴을 붙이면 문서 만들기가 멈춘다(F4-216 검토 B1).
type JsonScalar = bool | int | float | str | None
type JsonValue = JsonScalar | Sequence[JsonValue] | Mapping[str, JsonValue]


class BookIn(Schema):
    title: str
    note: JsonValue = None


class BookOut(Schema):
    id: int
    title: str


class BookShelfBusyError(Schema):
    error: str = "book_shelf_busy"
    message: str = "Shelf is busy."


router = Router()


@router.get("/books/{book_id}", auth=TokenAuth(), response={200: BookOut})
def get_book(request, book_id: int):
    return BookOut(id=book_id, title="t")


@router.post(
    "/books",
    auth=TokenAuth(),
    response={201: BookOut, 503: BookShelfBusyError},
    openapi_extra={"responses": {503: {"headers": {"Retry-After": {"schema": {"type": "integer"}}}}}},
)
def create_book(request, body: BookIn, response: HttpResponse):
    if body.title == "busy":
        response["Retry-After"] = "30"
        return Status(503, BookShelfBusyError())
    return Status(201, BookOut(id=1, title=body.title))


@router.get("/health", response={200: dict})
def health(request):
    return {"ok": True}


@router.get("/shelves/{code}", response={200: dict})
def shelf(request, code: str):
    return {"code": code}


@router.post("/webhook", response={200: dict})
def webhook(request):
    return {"ok": True}


@router.get("/webhook", response={200: dict})
def webhook_status(request):
    return {"ok": True}


@router.put("/webhook", response={200: dict})
def webhook_replace(request):
    return {"ok": True}


@router.get("/search", response={200: dict})
def search(request, q: str = ""):
    return {"q": q}


@router.get("/search-required", response={200: dict})
def search_required(request, q: str):
    return {"q": q}
