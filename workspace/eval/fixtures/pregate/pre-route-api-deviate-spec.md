# 미니 설계 명세 — 정해진 꼴 밖의 루트 API 클래스 (F4-173 pre-route 대조 픽스처)

`pre-route-add-api-spec.md` 와 같되 `get_openapi_schema` 서명이 정해진 꼴이 아니다(인자 없음). 이 계획대로 지으면
G2 에서도 #437 · #63 a 가 그 클래스를 막으므로, 스텁은 정해진 글로 바뀌지 않고 보통 스텁으로 남아 예보가 각 1건(진탐)을
낸다(G2 도 같다). 합성 저장소 = `pre-route-add-api-spec.md` 와 같다.

## 파일 계획

<!-- machine: file-plan -->
```paths
add	framework/ninja/pre_route_responses.py	# 경로 앞 응답 정본(플러그인 글 그대로)
add	config/api.py	# 루트 API(꼴 밖 서명)
```

## 공개 심볼

<!-- machine: symbols -->
```symbols
config/api.py::DocumentedAPI(NinjaExtraAPI)
config/api.py::DocumentedAPI.get_openapi_schema(self) -> OpenAPISchema
```

## 경계 import

<!-- machine: boundary-imports -->
```imports
config/api.py	from ninja_extra import NinjaExtraAPI
config/api.py	from ninja.openapi.schema import OpenAPISchema
config/api.py	from framework.ninja.pre_route_responses import add_pre_route_responses
```
