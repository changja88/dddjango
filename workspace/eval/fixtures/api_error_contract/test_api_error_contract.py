from __future__ import annotations

from enum import Enum
from io import BytesIO
from typing import ClassVar

import django
import pytest
from django.conf import settings
from django.http import (
    FileResponse,
    HttpResponse,
    HttpResponseRedirect,
    StreamingHttpResponse,
)
from django.test import Client
from django.urls import path
from pydantic import ValidationError


if not settings.configured:
    settings.configure(
        ALLOWED_HOSTS=["testserver"],
        DEBUG=False,
        INSTALLED_APPS=["ninja_extra"],
        ROOT_URLCONF=__name__,
        SECRET_KEY="api-error-contract-fixture",
    )
    django.setup()


from ninja import Schema, Status
from ninja.errors import AuthorizationError, HttpError
from ninja.security import HttpBearer
from ninja.throttling import BaseThrottle
from ninja_extra import ControllerBase, NinjaExtraAPI, api_controller, http_get


class InventoryErrorCode(str, Enum):
    ITEM_NOT_FOUND = "inventory.item_not_found"
    ITEM_CONFLICT = "inventory.item_conflict"


class ErrorOut(Schema):
    status: int
    code: str
    title: str
    detail: str


class InventoryErrorOut(ErrorOut):
    code: InventoryErrorCode


class ManagedInventoryErrorOut(InventoryErrorOut):
    managed: ClassVar[bool] = True
    approved_header: ClassVar[str] = "X-Inventory-Error"


class ItemNotFoundErrorOut(ManagedInventoryErrorOut):
    status: int = 404
    code: InventoryErrorCode = InventoryErrorCode.ITEM_NOT_FOUND
    title: str = "Inventory item not found"
    detail: str = "The requested inventory item does not exist."


class ItemConflictErrorOut(ManagedInventoryErrorOut):
    status: int = 409
    code: InventoryErrorCode = InventoryErrorCode.ITEM_CONFLICT
    title: str = "Inventory item conflict"
    detail: str = "The inventory item conflicts with current state."


class SuccessOut(Schema):
    status: int = 200
    item_id: int
    name: str


class DenyBearer(HttpBearer):
    last_result: ClassVar[object] = "not-called"

    def authenticate(self, request, token: str):
        type(self).last_result = None
        return None


class AlwaysThrottle(BaseThrottle):
    def allow_request(self, request) -> bool:
        return False

    def wait(self) -> int:
        return 7


deny_bearer = DenyBearer()


@api_controller("/inventory", auto_import=False)
class InventoryController(ControllerBase):
    @http_get(
        "/{item_id}",
        response={200: SuccessOut, 404: InventoryErrorOut, 409: InventoryErrorOut},
    )
    def get_item(self, item_id: int, response: HttpResponse):
        if item_id == 0:
            error = ItemNotFoundErrorOut()
            response[error.approved_header] = error.code.value
            return Status(error.status, error)
        if item_id == 9:
            error = ItemConflictErrorOut()
            response[error.approved_header] = error.code.value
            return Status(error.status, error)
        return Status(200, SuccessOut(item_id=item_id, name="stapler"))


@api_controller("/async-inventory", auto_import=False)
class AsyncInventoryController(ControllerBase):
    @http_get(
        "/{item_id}",
        response={200: SuccessOut, 404: InventoryErrorOut, 409: InventoryErrorOut},
    )
    async def get_item(self, item_id: int, response: HttpResponse):
        if item_id == 9:
            error = ItemConflictErrorOut()
            response[error.approved_header] = error.code.value
            return Status(error.status, error)
        return Status(200, SuccessOut(item_id=item_id, name="async stapler"))


@api_controller("/framework", auto_import=False)
class FrameworkController(ControllerBase):
    @http_get("/http-error")
    def http_error(self):
        raise HttpError(418, "framework http error")

    @http_get("/auth", auth=deny_bearer)
    def auth(self, request):
        return {"authenticated": True}

    @http_get("/forbidden")
    def forbidden(self):
        raise AuthorizationError()

    @http_get("/validated")
    def validated(self, limit: int):
        return {"limit": limit}

    @http_get("/throttled", throttle=AlwaysThrottle())
    def throttled(self):
        return {"allowed": True}

    @http_get("/unidentified")
    def unidentified(self):
        raise RuntimeError("private sentinel must not leak")


@api_controller("/native", auto_import=False)
class NativeResponseController(ControllerBase):
    @http_get("/file")
    def file(self):
        return FileResponse(BytesIO(b"file-body"), filename="fixture.txt")

    @http_get("/stream")
    def stream(self):
        return StreamingHttpResponse(iter([b"stream-", b"body"]))

    @http_get("/redirect")
    def redirect(self):
        return HttpResponseRedirect("/destination")

    @http_get("/empty", response={204: None})
    def empty(self):
        return Status(204, None)


@api_controller("/registration", auto_import=False)
class RegistrationProbeController(ControllerBase):
    @http_get("/probe", response=SuccessOut)
    def probe(self):
        return SuccessOut(item_id=77, name="explicit registrar")


def register_inventory_boundary(api: NinjaExtraAPI) -> None:
    api.register_controllers(
        InventoryController,
        AsyncInventoryController,
        FrameworkController,
        NativeResponseController,
        RegistrationProbeController,
    )


api = NinjaExtraAPI(urls_namespace="api_error_contract")
register_inventory_boundary(api)
urlpatterns = [path("api/", api.urls)]


@pytest.fixture
def client() -> Client:
    return Client(raise_request_exception=False)


def _managed_error_types() -> set[type[ManagedInventoryErrorOut]]:
    pending = list(ManagedInventoryErrorOut.__subclasses__())
    concrete: set[type[ManagedInventoryErrorOut]] = set()
    while pending:
        error_type = pending.pop()
        children = error_type.__subclasses__()
        if children:
            pending.extend(children)
        else:
            concrete.add(error_type)
    return concrete


def _assert_not_bc_error(response) -> None:
    assert response.headers.get("X-Inventory-Error") is None
    has_json_body = (
        response.headers.get("Content-Type", "").startswith("application/json")
        and not response.streaming
        and bool(response.content)
    )
    if has_json_body:
        body = response.json()
        assert not (
            isinstance(body, dict)
            and set(body) == {"status", "code", "title", "detail"}
            and str(body.get("code", "")).startswith("inventory.")
        )


def test_managed_concrete_errors_keep_zero_argument_construction() -> None:
    error_types = _managed_error_types()

    assert error_types == {ItemNotFoundErrorOut, ItemConflictErrorOut}
    assert {error_type().status for error_type in error_types} == {404, 409}


def test_bc_enum_rejects_foreign_code_and_common_schema_keeps_exact_contract() -> None:
    with pytest.raises(ValidationError):
        InventoryErrorOut(
            status=400,
            code="payments.card_declined",
            title="Wrong boundary",
            detail="This code belongs to a different bounded context.",
        )

    assert set(ErrorOut.model_fields) == {"status", "code", "title", "detail"}
    assert {name for name, field in ErrorOut.model_fields.items() if field.is_required()} == {
        "status",
        "code",
        "title",
        "detail",
    }
    assert {name: field.annotation for name, field in ErrorOut.model_fields.items()} == {
        "status": int,
        "code": str,
        "title": str,
        "detail": str,
    }


def test_status_wrapper_and_success_body_status_coexist_on_multi_response(client) -> None:
    response = client.get("/api/inventory/7")

    assert response.status_code == 200
    assert response.json() == {"status": 200, "item_id": 7, "name": "stapler"}


def test_sync_controller_serializes_status_wrapped_managed_error(client) -> None:
    response = client.get("/api/inventory/0")

    assert response.status_code == 404
    assert response.headers["X-Inventory-Error"] == "inventory.item_not_found"
    assert response.json() == {
        "status": 404,
        "code": "inventory.item_not_found",
        "title": "Inventory item not found",
        "detail": "The requested inventory item does not exist.",
    }


def test_async_controller_serializes_status_wrapped_managed_error(client) -> None:
    response = client.get("/api/async-inventory/9")

    assert response.status_code == 409
    assert response.headers["X-Inventory-Error"] == "inventory.item_conflict"
    assert response.json() == {
        "status": 409,
        "code": "inventory.item_conflict",
        "title": "Inventory item conflict",
        "detail": "The inventory item conflicts with current state.",
    }


def test_auth_failure_never_stores_error_schema_in_request_auth(client) -> None:
    response = client.get(
        "/api/framework/auth", HTTP_AUTHORIZATION="Bearer rejected-token"
    )

    assert response.status_code == 401
    assert DenyBearer.last_result is None
    assert getattr(response.wsgi_request, "auth", None) is None
    assert not isinstance(getattr(response.wsgi_request, "auth", None), ErrorOut)
    _assert_not_bc_error(response)


def test_general_http_error_stays_framework_shaped(client) -> None:
    response = client.get("/api/framework/http-error")

    assert response.status_code == 418
    _assert_not_bc_error(response)


def test_default_401_and_403_stay_framework_shaped(client) -> None:
    unauthorized = client.get("/api/framework/auth")
    forbidden = client.get("/api/framework/forbidden")

    assert unauthorized.status_code == 401
    assert unauthorized.headers.get("WWW-Authenticate") is None
    _assert_not_bc_error(unauthorized)
    assert forbidden.status_code == 403
    _assert_not_bc_error(forbidden)


def test_route_404_and_validation_422_stay_framework_shaped(client) -> None:
    missing = client.get("/api/no-such-route")
    invalid = client.get("/api/framework/validated", {"limit": "not-an-integer"})

    assert missing.status_code == 404
    _assert_not_bc_error(missing)
    assert invalid.status_code == 422
    _assert_not_bc_error(invalid)


def test_throttle_429_stays_framework_shaped_and_records_default_header(client) -> None:
    response = client.get("/api/framework/throttled")

    assert response.status_code == 429
    assert response.headers.get("Retry-After") == "7"
    _assert_not_bc_error(response)


def test_unidentified_500_hides_traceback_with_debug_disabled(client) -> None:
    response = client.get("/api/framework/unidentified")

    assert settings.DEBUG is False
    assert response.status_code == 500
    assert b"Traceback" not in response.content
    assert b"private sentinel must not leak" not in response.content
    _assert_not_bc_error(response)


def test_native_http_responses_are_not_coerced_to_error_schemas(client) -> None:
    file_response = client.get("/api/native/file")
    stream_response = client.get("/api/native/stream")
    redirect_response = client.get("/api/native/redirect")
    empty_response = client.get("/api/native/empty")

    assert file_response.status_code == 200
    assert b"".join(file_response.streaming_content) == b"file-body"
    assert b"".join(stream_response.streaming_content) == b"stream-body"
    assert redirect_response.status_code == 302
    assert redirect_response.headers["Location"] == "/destination"
    assert empty_response.status_code == 204
    assert empty_response.content == b""
    for response in (file_response, stream_response, redirect_response, empty_response):
        _assert_not_bc_error(response)


def test_project_urlconf_explicit_registrar_mounts_controller(client) -> None:
    response = client.get("/api/registration/probe")

    assert response.status_code == 200
    assert response.json() == {
        "status": 200,
        "item_id": 77,
        "name": "explicit registrar",
    }


def test_openapi_advertises_only_direct_bc_error_responses_as_bc_schema(client) -> None:
    response = client.get("/api/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    inventory_get = paths["/api/inventory/{item_id}"]["get"]
    for status in ("404", "409"):
        schema = inventory_get["responses"][status]["content"]["application/json"][
            "schema"
        ]
        assert schema == {"$ref": "#/components/schemas/InventoryErrorOut"}

    framework_paths = {
        route: operation
        for route, operation in paths.items()
        if route.startswith("/api/framework/")
    }
    assert framework_paths
    assert "InventoryErrorOut" not in str(framework_paths)
    assert "ItemNotFoundErrorOut" not in str(framework_paths)
    assert "ItemConflictErrorOut" not in str(framework_paths)
