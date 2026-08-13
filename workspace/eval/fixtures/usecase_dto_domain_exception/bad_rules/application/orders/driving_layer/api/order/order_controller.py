from application.orders.application_layer.order.place_order.place_order_result import PlaceOrderResult
from application.orders.domain_layer.order.exception.order_not_payable import decide_eligibility  # 세탁 ⑴: 예외 칸의 함수
from application.orders.domain_layer.order.exception import SmuggledOrder  # 세탁 ⑵: __init__ 재수출


def handle(result: PlaceOrderResult) -> dict:
    if decide_eligibility(1):
        return {"id": result.order_id, "kind": SmuggledOrder.__name__}
    return {"error": "no"}
