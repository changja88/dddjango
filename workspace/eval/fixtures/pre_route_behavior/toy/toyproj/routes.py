"""루트 API 넷에 경로를 단다 — 클래스 · 함수 · API · Router 인증, 같은 Router 두 번(차례 둘), 중첩 Router, ninja_extra 컨트롤러."""
from books.controller import router as books
from extra.controller import TokenAuth, router as extra, secured
from joins.controllers import ClosedController, PermissionControllers, PublicController, ThrottleControllers
from joins.routes import api_level, conv, dup, multi, parent, shared, shared_b
from toyproj.api import api, api2, apib
from toyproj.extra_api import api3

api.add_router("/", books)
api.add_router("/x", extra)
api.add_router("/s", secured)
api.add_router("/public", shared, auth=None, url_name_prefix="public")
api.add_router("/private", shared, auth=TokenAuth(), url_name_prefix="private")
api.add_router("/p", parent)
api.add_router("/dup", dup)
api.add_router("/conv", conv)

api2.add_router("/", api_level)

apib.add_router("/private", shared_b, auth=TokenAuth(), url_name_prefix="private")
apib.add_router("/public", shared_b, auth=None, url_name_prefix="public")
apib.add_router("/m", multi)

api3.register_controllers(*PermissionControllers, PublicController, ClosedController, *ThrottleControllers)
