from application.orders.application_layer.order.place_order.place_order_use_case import PlaceOrderUseCase
from application.orders.domain_layer.order.exception.out_of_stock import OutOfStock
from .contract.request.get_order_request import GetOrderRequest
from .contract.response.get_order_response import GetOrderResponse
from .contract.exception.lookup_unavailable import LookupUnavailable


def get_order_query(request: GetOrderRequest) -> GetOrderResponse:
    use_case = PlaceOrderUseCase()
    try:
        result = use_case.execute(request.order_id)
    except OutOfStock:
        raise LookupUnavailable()
    return GetOrderResponse(code="OK", order_id=request.order_id)
