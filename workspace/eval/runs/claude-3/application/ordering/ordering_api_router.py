"""ordering 앱 API 라우터 진입점 (명세 §4.1·§4.3).

NinjaAPI 인스턴스를 생성하고 place_order 라우터를 등록한다. 루트 config/urls 가
이 api 를 /api/ 프리픽스로 마운트한다(무버전 — 명세 §2.3 api minor m5).
에러 계약(409/404/422/415/400)은 problem+json 으로 중앙 변환한다(명세 §2.3·§4.5).
"""
from ninja import NinjaAPI

from application.ordering.presentation_layer.api.place_order.api_order import (
    router as place_order_router,
)
from application.ordering.presentation_layer.api.problem_detail import (
    register_problem_handlers,
)

api = NinjaAPI(title="Ordering API")
api.add_router("/", place_order_router)
register_problem_handlers(api)
