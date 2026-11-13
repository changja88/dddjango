# 미니 설계 명세 — 경로 앞 응답 꼴 세우기 (F4-173 pre-route 픽스처)

기존 루트 API(`config/api.py` · 평범한 `NinjaExtraAPI`)와 경로 하나(`GET /orders/{order_id}`)가 있는 저장소에
경로 앞 응답 꼴을 세운다 — 정본 파일 · 표를 더하고 루트 API 를 정해진 클래스로 바꾼다(implementation-django-ninja
§6.2 «경로 앞 응답»). 정본은 플러그인 글 그대로 서고 표는 사본에 세우지 않으며 `update` 는 미시뮬레이션이라, 예보는
G2 처럼 #63 귀속 0 이다. 합성 저장소 = `mini_repo` + `pre_route_overlay/`.

## 파일 계획

<!-- machine: file-plan -->
```paths
add	framework/ninja/pre_route_responses.py	# 경로 앞 응답 정본(플러그인 글 그대로)
add	framework/ninja/pre_route_response_table.py	# 경로 앞 응답 표(G1 승인 행)
update	config/api.py	# 루트 API 를 정해진 클래스로
```

## 공개 심볼

<!-- machine: symbols -->
```symbols
framework/ninja/pre_route_responses.py::add_pre_route_responses(api: NinjaAPI, schema: OpenAPISchema) -> OpenAPISchema
framework/ninja/pre_route_response_table.py::ServiceMaintenanceOut(Schema) {error: str, message: str}
config/api.py::DocumentedAPI(NinjaExtraAPI)
config/api.py::DocumentedAPI.get_openapi_schema(self, *, path_prefix: str | None = None, path_params: dict[str, object] | None = None) -> OpenAPISchema
```

## 경계 import

<!-- machine: boundary-imports -->
```imports
framework/ninja/pre_route_responses.py	from ninja import NinjaAPI
framework/ninja/pre_route_responses.py	from ninja.openapi.schema import OpenAPISchema
framework/ninja/pre_route_responses.py	from framework.ninja.pre_route_response_table import BAD_REQUEST_RESPONSE, PRE_ROUTE_RESPONSES
framework/ninja/pre_route_response_table.py	from ninja import Schema
config/api.py	from framework.ninja.pre_route_responses import add_pre_route_responses
```
