"""경로 앞 응답을 문서에 붙인다 — dddjango 플러그인 정본(고치지 않는다).

경로 코드보다 먼저 답하는 쪽(Ninja 인증 · CSRF · 권한 · throttle · 입력 해석 · Django 상한 ·
미들웨어(서드파티 포함) · 앞단)이 보내는 오류를 경로마다 생성 문서의 응답 항목으로 더한다.
프로젝트 몫은 `framework/ninja/pre_route_response_table.py` 의 표다.
"""
import copy
import re
from typing import Literal, NotRequired, TypedDict

from django.conf import settings
from ninja import NinjaAPI, Schema
from ninja.openapi.schema import OpenAPISchema
from ninja.operation import Operation
from ninja.utils import normalize_path
from pydantic import JsonValue, TypeAdapter

from framework.ninja.pre_route_response_table import BAD_REQUEST_RESPONSE, PRE_ROUTE_RESPONSES

type When = Literal["all", "auth", "csrf", "permission", "throttle", "json_body", "body", "query", "input"]
type OpenAPIObject = dict[str, JsonValue]


class PreRouteResponse(TypedDict):
    status: int
    when: When
    description: str
    body: NotRequired[type[Schema]]
    media_type: NotRequired[str]
    methods: NotRequired[tuple[str, ...]]
    namespaces: NotRequired[tuple[str, ...]]
    operations: NotRequired[tuple[str, ...]]
    exempt: NotRequired[tuple[str | None, str]]
    headers: NotRequired[dict[str, JsonValue]]


class BadRequestResponse(TypedDict):
    media_type: str
    body: NotRequired[type[Schema]]


class OperationFact(TypedDict):
    auth: bool
    csrf: bool
    throttle: bool
    permission: bool
    converters: dict[str, str]


class NinjaDetailOut(Schema):
    detail: str


class NinjaValidationItemOut(Schema):
    type: str
    loc: list[str | int]
    msg: str


class NinjaValidationOut(Schema):
    detail: list[NinjaValidationItemOut]


HTTP_METHODS: frozenset[str] = frozenset({"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"})
UNSAFE_METHODS: frozenset[str] = frozenset({"POST", "PUT", "PATCH", "DELETE"})
REF_TEMPLATE: str = "#/components/schemas/{model}"
CONVERTER_PARAMETER: re.Pattern[str] = re.compile(r"{(\w+):(\w+)}")
OPERATION_KEY: re.Pattern[str] = re.compile(r"(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS) /\S*")
IGNORED_SCHEMA_KEYS: frozenset[str] = frozenset({"title", "description", "default", "examples", "example"})
CONVERTER_SCHEMA: dict[str, dict[str, str]] = {
    "int": {"type": "integer"},
    "uuid": {"type": "string", "format": "uuid"},
    "uuidstr": {"type": "string", "format": "uuid"},
    "str": {"type": "string"},
    "slug": {"type": "string"},
    "path": {"type": "string"},
}
ROW_KEYS: frozenset[str] = PreRouteResponse.__required_keys__ | PreRouteResponse.__optional_keys__
NINJA_RESPONSES: tuple[PreRouteResponse, ...] = (
    {"status": 401, "when": "auth", "description": "인증 실패", "body": NinjaDetailOut},
    {"status": 403, "when": "csrf", "description": "CSRF 확인 실패", "body": NinjaDetailOut},
    {"status": 403, "when": "permission", "description": "권한 없음", "body": NinjaDetailOut},
    {
        "status": 429,
        "when": "throttle",
        "description": "요청이 너무 잦음",
        "body": NinjaDetailOut,
        "headers": {"Retry-After": {"schema": {"type": "integer"}}},
    },
    {"status": 400, "when": "json_body", "description": "몸통을 읽을 수 없음", "body": NinjaDetailOut},
    {"status": 422, "when": "input", "description": "입력 검증 실패", "body": NinjaValidationOut},
)


def add_pre_route_responses(api: NinjaAPI, schema: OpenAPISchema) -> OpenAPISchema:
    rows: tuple[PreRouteResponse, ...] = (*NINJA_RESPONSES, *_django_rows(), *_project_rows())
    facts: dict[str, OperationFact] = _operation_facts(api, schema.path_prefix)
    components: dict[str, JsonValue] = schema.setdefault("components", {}).setdefault("schemas", {})
    paths: dict[str, dict[str, OpenAPIObject]] = schema.get("paths", {})
    keys: set[str] = set()
    for path, item in paths.items():
        for method in list(item):
            operation: OpenAPIObject = copy.deepcopy(item[method])
            item[method] = operation
            key: str = f"{method.upper()} {path}"
            keys.add(key)
            fact: OperationFact | None = facts.get(key)
            if fact is None:
                raise ValueError(f"pre-route operation not joined: {key}")
            for entry in rows:
                if _applies(entry, operation, fact, key, path, method.upper(), api.urls_namespace):
                    _add(operation, entry, components)
    for entry in rows:
        if api.urls_namespace in entry.get("namespaces", ()):
            for target in entry.get("operations", ()):
                if target not in keys:
                    raise ValueError(f"pre-route operation not in this document: {target}")
    return schema


def _django_rows() -> tuple[PreRouteResponse, ...]:
    bad_request: BadRequestResponse = TypeAdapter(BadRequestResponse).validate_python(BAD_REQUEST_RESPONSE, strict=True)
    rows: list[PreRouteResponse] = []
    limits: tuple[tuple[When, str], ...] = (("body", "몸통이 Django 상한을 넘음"), ("query", "쿼리 칸 수가 Django 상한을 넘음"))
    for when, description in limits:
        row: PreRouteResponse = {"status": 400, "when": when, "description": description, "media_type": bad_request["media_type"]}
        if "body" in bad_request:
            row["body"] = bad_request["body"]
        rows.append(row)
    return tuple(rows)


def _project_rows() -> tuple[PreRouteResponse, ...]:
    for raw in PRE_ROUTE_RESPONSES:
        unknown: set[str] = set(raw) - ROW_KEYS
        if unknown:
            raise ValueError(f"unknown pre-route row keys: {sorted(unknown)}")
    rows: tuple[PreRouteResponse, ...] = TypeAdapter(tuple[PreRouteResponse, ...]).validate_python(
        PRE_ROUTE_RESPONSES, strict=True
    )
    for row in rows:
        if not 400 <= row["status"] <= 599:
            raise ValueError(f"pre-route status out of 400-599: {row['status']}")
        for values in (row.get("methods"), row.get("namespaces"), row.get("operations")):
            if values is not None and not values:
                raise ValueError(f"empty narrowing tuple in pre-route row {row['status']}")
        if not set(row.get("methods", ())) <= HTTP_METHODS:
            raise ValueError(f"pre-route methods must be upper-case HTTP methods: {row['methods']}")
        if "operations" in row:
            if len(row.get("namespaces", ())) != 1:
                raise ValueError(f"pre-route row {row['status']} with operations needs exactly one namespace")
            for target in row["operations"]:
                if OPERATION_KEY.fullmatch(target) is None:
                    raise ValueError(f"pre-route operation must be 'METHOD /path': {target}")
    return rows


def _operation_facts(api: NinjaAPI, path_prefix: str) -> dict[str, OperationFact]:
    facts: dict[str, OperationFact] = {}
    for router in api._get_bound_routers():
        for raw_path, path_view in router.path_operations.items():
            joined: str = normalize_path("/" + path_prefix + "/".join(i for i in (router.prefix, raw_path) if i))
            converters: dict[str, str] = {name: kind for kind, name in CONVERTER_PARAMETER.findall(joined)}
            doc_path: str = re.sub(r"{[^}:]+:", "{", joined)
            for operation in path_view.operations:
                if not operation.include_in_schema:
                    continue
                for method in operation.methods:
                    facts[f"{method.upper()} {doc_path}"] = {
                        "auth": bool(operation.auth_callbacks),
                        "csrf": not operation.csrf_exempt
                        and any(getattr(callback, "csrf", False) for callback in operation.auth_callbacks),
                        "throttle": bool(operation.throttle_objects),
                        "permission": _has_permission(operation),
                        "converters": converters,
                    }
    return facts


def _has_permission(operation: Operation) -> bool:
    get_route_function: object = getattr(operation.view_func, "get_route_function", None)
    if not callable(get_route_function):
        return False
    route_function: object = get_route_function()
    route: object = getattr(route_function, "route", None)
    controller: object = getattr(route_function, "api_controller", None)
    permissions: object = getattr(route, "permissions", None) or getattr(controller, "permission_classes", None) or ()
    if not isinstance(permissions, (list, tuple)):
        return False
    return any(not _allows_any(permission) for permission in permissions)


def _allows_any(permission: object) -> bool:
    kind: type = permission if isinstance(permission, type) else type(permission)
    for base in kind.__mro__:
        if base.__name__ == "AllowAny":
            return getattr(kind, "has_permission", None) is getattr(base, "has_permission", None)
    return False


def _applies(
    entry: PreRouteResponse, operation: OpenAPIObject, fact: OperationFact, key: str, path: str, method: str, namespace: str
) -> bool:
    body: JsonValue = operation.get("requestBody")
    parameters: JsonValue = operation.get("parameters", [])
    content: JsonValue = body.get("content") if isinstance(body, dict) else None
    listed: list[dict[str, JsonValue]] = [p for p in parameters if isinstance(p, dict)] if isinstance(parameters, list) else []
    checks: dict[When, bool] = {
        "all": True,
        "auth": fact["auth"],
        "csrf": fact["csrf"] and method in UNSAFE_METHODS,
        "permission": fact["permission"],
        "throttle": fact["throttle"],
        "body": isinstance(body, dict),
        "json_body": isinstance(content, dict) and "application/json" in content,
        "query": any(p.get("in") == "query" for p in listed),
        "input": isinstance(body, dict) or any(_can_fail(p, fact["converters"]) for p in listed),
    }
    if not checks[entry["when"]]:
        return False
    if method not in entry.get("methods", (method,)):
        return False
    if namespace not in entry.get("namespaces", (namespace,)):
        return False
    if "operations" in entry and key not in entry["operations"]:
        return False
    exempt: tuple[str | None, str] | None = entry.get("exempt")
    if exempt is not None:
        only_method, setting_name = exempt
        exempt_paths: object = getattr(settings, setting_name)
        if (only_method is None or only_method == method) and isinstance(exempt_paths, (list, tuple)) and path in exempt_paths:
            return False
    return True


def _can_fail(parameter: dict[str, JsonValue], converters: dict[str, str]) -> bool:
    schema: JsonValue = parameter.get("schema", {})
    if not isinstance(schema, dict):
        return True
    converter: str | None = converters.get(str(parameter.get("name"))) if parameter.get("in") == "path" else None
    if converter is not None:
        return CONVERTER_SCHEMA.get(converter) != {k: v for k, v in schema.items() if k not in IGNORED_SCHEMA_KEYS}
    plain: bool = _plain(schema)
    if parameter.get("in") == "path":
        return not plain
    return parameter.get("required", False) is True or not plain


def _plain(schema: dict[str, JsonValue]) -> bool:
    keys: set[str] = set(schema) - IGNORED_SCHEMA_KEYS
    options: JsonValue = schema.get("anyOf")
    items: JsonValue = schema.get("items")
    if keys == {"type"}:
        return schema["type"] == "string"
    if keys == {"anyOf"} and isinstance(options, list):
        return all(o == {"type": "null"} or (isinstance(o, dict) and _plain(o)) for o in options)
    if keys == {"type", "items"} and schema["type"] == "array":
        return isinstance(items, dict) and _plain(items)
    return False


def _add(operation: OpenAPIObject, entry: PreRouteResponse, components: dict[str, JsonValue]) -> None:
    responses: dict[int, OpenAPIObject] = operation.setdefault("responses", {})  # type: ignore[assignment]
    status: int = entry["status"]
    content: dict[str, JsonValue] = _content(entry, components)
    headers: dict[str, JsonValue] = entry.get("headers", {})
    existing: OpenAPIObject | None = responses.get(status)
    if existing is None:
        added: OpenAPIObject = {"description": entry["description"], "content": content}
        if headers:
            added["headers"] = dict(headers)
        responses[status] = added
        return
    current_content: dict[str, JsonValue] = existing.setdefault("content", {})  # type: ignore[assignment]
    for media_type, item in content.items():
        current: JsonValue = current_content.get(media_type)
        if not isinstance(current, dict) or not isinstance(item, dict):
            current_content[media_type] = item
            continue
        if item["schema"] != current["schema"]:
            old: JsonValue = current["schema"]
            options: list[JsonValue] = old["anyOf"] if isinstance(old, dict) and isinstance(old.get("anyOf"), list) else [old]  # type: ignore[assignment]
            if item["schema"] not in options:
                current["schema"] = {"anyOf": [*options, item["schema"]]}
    if headers:
        existing_headers: dict[str, JsonValue] = existing.setdefault("headers", {})  # type: ignore[assignment]
        for name, header in headers.items():
            existing_headers.setdefault(name, header)
    existing["description"] = f'{existing.get("description", "")} · {entry["description"]}'.lstrip(" ·")


def _content(entry: PreRouteResponse, components: dict[str, JsonValue]) -> dict[str, JsonValue]:
    media_type: str = entry.get("media_type", "application/json")
    body: type[Schema] | None = entry.get("body")
    if body is None:
        return {media_type: {"schema": {"type": "string"}}}
    schema: dict[str, JsonValue] = body.model_json_schema(ref_template=REF_TEMPLATE, mode="serialization")
    definitions: JsonValue = schema.pop("$defs", {})
    for name, definition in {**(definitions if isinstance(definitions, dict) else {}), body.__name__: schema}.items():
        if components.setdefault(name, definition) != definition:
            raise ValueError(f"component name collision: {name}")
    return {media_type: {"schema": {"$ref": REF_TEMPLATE.format(model=body.__name__)}}}
