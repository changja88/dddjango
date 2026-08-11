from ninja_extra import api_controller, http_get

from application.orders.application_layer.order.get_order.get_order_query import GetOrderQuery
from application.orders.domain_layer.order.exception.order_not_found import OrderNotFound
from application.orders.driving_layer.api.bc_error_schema import OrdersErrorCode, OrdersErrorSchema


@api_controller("/orders")
class OrderController:
    @http_get("/{order_id}", response={200: dict, 404: OrdersErrorSchema})
    def get_order(self, order_id: str):
        try:
            result = self._use_case.execute(GetOrderQuery(order_id=order_id))
        except OrderNotFound:
            return 404, OrdersErrorSchema(code=OrdersErrorCode.ORDER_NOT_FOUND, message="order not found")
        return 200, {"order_id": order_id}
