# 미니 설계 명세 — orders BC 가격 조회 슬라이스 (red 픽스처)

의도된 위반 3건을 심은 명세 — pre-gate 가 정확히 그 귀속을 예보해야 한다:

1. 트리 밖 칸: `application/orders/reporting/` — BC 직계 여덟째(#81).
2. 값 객체 파일에 공개 클래스 2개: `price.py` 의 `Price`·`Currency` (#267).
3. OHS contract 칸의 pydantic import: `quote_request.py` (#472 — contract 는
   표준 라이브러리·같은 BC 계약만).

## 파일 계획

<!-- machine: file-plan -->
```paths
add	application/orders/reporting/report_builder.py	# 의도 위반 ① 트리 밖 칸
add	application/orders/domain_layer/shared_value_object/price.py	# 의도 위반 ② 2클래스
add	application/orders/driving_layer/open_host_service/pricing/pricing_service.py
add	application/orders/driving_layer/open_host_service/pricing/contract/request/quote_request.py	# 의도 위반 ③
empty	application/orders/driving_layer/open_host_service/pricing/contract/response/__init__.py
empty	application/orders/driving_layer/open_host_service/pricing/contract/exception/pricing_published_error.py
```

## 공개 심볼

<!-- machine: symbols -->
```symbols
application/orders/reporting/report_builder.py::ReportBuilder
application/orders/domain_layer/shared_value_object/price.py::Price {amount: int, currency: str}
application/orders/domain_layer/shared_value_object/price.py::Currency {code: str}
application/orders/driving_layer/open_host_service/pricing/pricing_service.py::quote_query(request: QuoteRequest) -> object
application/orders/driving_layer/open_host_service/pricing/contract/request/quote_request.py::QuoteRequest(BaseModel) {amount: int, currency: str}
```

## 경계 import

<!-- machine: boundary-imports -->
```imports
application/orders/driving_layer/open_host_service/pricing/contract/request/quote_request.py	from pydantic import BaseModel
```
