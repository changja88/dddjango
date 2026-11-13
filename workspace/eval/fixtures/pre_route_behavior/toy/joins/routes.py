from django.views.decorators.csrf import csrf_exempt
from ninja import Path, Router
from ninja.security import django_auth
from ninja.throttling import AnonRateThrottle

from extra.controller import TokenAuth

# 같은 Router 를 두 번(공개 · 인증) — api 는 공개 쪽을 먼저, apib 는 인증 쪽을 먼저 단다
shared = Router()


@shared.get("/item", response={200: dict})
def shared_item(request):
    return {"ok": True}


shared_b = Router()


@shared_b.get("/item", response={200: dict})
def shared_b_item(request):
    return {"ok": True}


# Router 중첩 — 부모에 인증 · throttle
parent = Router(auth=TokenAuth(), throttle=AnonRateThrottle("1/m"))
child = Router()


@child.get("/leaf", response={200: dict})
def nested_leaf(request):
    return {"ok": True}


parent.add_router("/child", child)

# 사용자가 준 operation_id 가 겹침 — 한쪽만 인증
dup = Router()


@dup.get("/open", operation_id="same_id", response={200: dict})
def dup_open(request):
    return {"ok": True}


@dup.get("/closed", operation_id="same_id", auth=TokenAuth(), response={200: dict})
def dup_closed(request):
    return {"ok": True}


# 변환기 + 값 제약 · 변환기와 다른 타입 · 쿠키 인증 + csrf_exempt
conv = Router()


@conv.get("/positive/{int:book_id}", response={200: dict})
def positive(request, book_id: int = Path(..., gt=0)):
    return {"id": book_id}


@conv.get("/slug-int/{slug:code}", response={200: dict})
def slug_int(request, code: int):
    return {"code": code}


@conv.post("/session-exempt", auth=django_auth, response={200: dict})
@csrf_exempt
def session_exempt(request):
    return {"ok": True}


# 여러 메서드 한 operation — 쿠키 인증(POST 만 CSRF)
multi = Router()


@multi.api_operation(["GET", "POST"], "/both", auth=django_auth, response={200: dict})
def both(request):
    return {"ok": True}


# API 단위 쿠키 인증(api2) — auth=None 으로 끈 경로 · POST 의 CSRF
api_level = Router()


@api_level.get("/api-auth", response={200: dict})
def api_auth(request):
    return {"ok": True}


@api_level.get("/api-auth-off", auth=None, response={200: dict})
def api_auth_off(request):
    return {"ok": True}


@api_level.post("/api-auth-post", response={200: dict})
def api_auth_post(request):
    return {"ok": True}
