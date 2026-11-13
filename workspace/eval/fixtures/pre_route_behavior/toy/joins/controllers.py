from django.http import HttpRequest
from ninja_extra import api_controller, route
from ninja_extra.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from ninja_extra.throttling import AnonRateThrottle as ExtraAnon, throttle as extra_throttle

from extra.controller import TokenAuth


@api_controller("/ctl", auth=TokenAuth(), permissions=[IsAuthenticated])
class AuthController:
    @route.get("/a", response={200: dict})
    def a(self):
        return {"ok": True}


class StaffOnly(IsAuthenticated):
    def has_permission(self, request, controller):
        return False


@api_controller("/perm", auth=TokenAuth(), permissions=[StaffOnly])
class StaffController:
    @route.get("/b", response={200: dict})
    def b(self):
        return {"ok": True}


@api_controller("/noauth", permissions=[IsAuthenticated])
class NoAuthController:
    @route.get("/c", response={200: dict})
    def c(self):
        return {"ok": True}


PermissionControllers = (AuthController, StaffController, NoAuthController)


# AllowAny 상속 — 바꾸지 않은 것(누구나) · has_permission 을 바꾼 것(막을 수 있다)
class Public(AllowAny):
    pass


class PublicButClosed(AllowAny):
    def has_permission(self, request: HttpRequest, controller) -> bool:
        return False


@api_controller("/pub", permissions=[Public])
class PublicController:
    @route.get("/list", response={200: dict})
    def list(self):
        return {"ok": True}

    @route.get("/ro", permissions=[IsAuthenticatedOrReadOnly], response={200: dict})
    def ro(self):
        return {"ok": True}

    @route.get("/either", permissions=[IsAuthenticated | AllowAny], response={200: dict})
    def either(self):
        return {"ok": True}


@api_controller("/closed", permissions=[PublicButClosed])
class ClosedController:
    @route.get("/x", response={200: dict})
    def x(self):
        return {"ok": True}


# throttle — 컨트롤러 비율(1/m) · 기본 비율 없는 데코레이터
@api_controller("/thr", throttle=[ExtraAnon(rate="1/m")])
class RateController:
    @route.get("/a", response={200: dict})
    def a(self):
        return {"ok": True}


@api_controller("/thr2")
class DefaultRateController:
    @route.get("/b", response={200: dict})
    @extra_throttle
    def b(self):
        return {"ok": True}


ThrottleControllers = (RateController, DefaultRateController)
