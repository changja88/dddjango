from application.orders.application_layer.order.place_order.place_order_result import PlaceOrderResult
from application.orders.domain_layer.order.exception.order_not_payable import OrderNotPayable  # 면제: 실선언 예외 클래스(#95)
from application.orders.domain_layer.order.exception.payment.payment_declined import PaymentDeclined  # 면제: 예외 칸 묶음 안 실선언 예외 클래스(#95 · #654~#656)


def handle(result: PlaceOrderResult) -> dict:
    try:
        return {"id": result.order_id}
    except OrderNotPayable:
        return {"error": "order-not-payable"}
    except PaymentDeclined:
        return {"error": "payment-declined"}
