from application.orders.application_layer.order.place_order.place_order_result import PlaceOrderResult
from application.orders.domain_layer.order.exception.order_not_payable import OrderNotPayable  # 면제: 실선언 예외 클래스(#95)


def handle(result: PlaceOrderResult) -> dict:
    try:
        return {"id": result.order_id}
    except OrderNotPayable:
        return {"error": "order-not-payable"}
