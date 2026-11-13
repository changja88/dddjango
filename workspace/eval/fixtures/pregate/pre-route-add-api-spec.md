# 미니 설계 명세 — 루트 API 를 새로 짓기 (F4-173 pre-route 픽스처)

루트 API 모듈이 없는 저장소에 `config/api.py` 를 정해진 클래스로 새로 짓고 정본 · 표를 더한다. 정해진 서명의
`get_openapi_schema` 하나뿐인 클래스 스텁은 정해진 메서드 글로 렌더되고, 그 글이 읽는 이름(`NinjaExtraAPI` ·
`OpenAPISchema`)은 전사 import 가 묶지 않으니 정형 import 로 보충된다(`add_pre_route_responses` 는 전사가 묶는다) —
예보는 G2 처럼 #63 · #437 귀속 0 이다. 합성 저장소 = `mini_repo` + `pre_route_overlay/` 에서 `config/api.py` 를 뺀 것.

## 파일 계획

<!-- machine: file-plan -->
```paths
add	framework/ninja/pre_route_responses.py	# 경로 앞 응답 정본(플러그인 글 그대로)
add	framework/ninja/pre_route_response_table.py	# 경로 앞 응답 표(G1 승인 행)
add	config/api.py	# 루트 API(정해진 클래스)
```

## 공개 심볼

<!-- machine: symbols -->
```symbols
framework/ninja/pre_route_response_table.py::ServiceMaintenanceOut(Schema) {error: str, message: str}
config/api.py::DocumentedAPI(NinjaExtraAPI)
config/api.py::DocumentedAPI.get_openapi_schema(*, path_prefix: str | None = None, path_params: dict[str, object] | None = None) -> OpenAPISchema
```

## 경계 import

<!-- machine: boundary-imports -->
```imports
framework/ninja/pre_route_response_table.py	from ninja import Schema
config/api.py	from framework.ninja.pre_route_responses import add_pre_route_responses
```
