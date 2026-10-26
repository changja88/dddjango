from application.orders.application_layer.order.place_order.place_order_result import PlaceOrderResult
from application.orders.domain_layer.order.exception.order_not_payable import decide_eligibility  # 세탁 ⑴: 예외 칸의 함수
from application.orders.domain_layer.order.exception import SmuggledOrder  # 세탁 ⑵: __init__ 재수출
from application.orders.domain_layer.domain_service.exception.fee.fee_rejected import FeeRejected  # 세탁 ⑶: 예외 칸 묶음이 아닌 한 칸
from application.orders.domain_layer.order.exception.payment.card.card_declined import CardDeclined  # 세탁 ⑷: 두 칸


def handle(result: PlaceOrderResult) -> dict:
    if decide_eligibility(1):
        return {"id": result.order_id, "kind": SmuggledOrder.__name__, "fee": FeeRejected.__name__, "card": CardDeclined.__name__}
    return {"error": "no"}
