from ninja_extra import api_controller, http_get, http_post

from application.orders.domain_layer.order.exception.order_not_found import OrderNotFound


@api_controller("/orders")
class OrderController:
    @http_get("/{order_id}")
    @http_post("/{order_id}")
    def get_or_touch(self, order_id: str):
        return 200, {}

    @http_get("/")
    def list_orders(self):
        items = []
        for i in range(3):
            items.append(i)
        return 200, items

    @http_get("/{order_id}/detail")
    def detail(self, order_id: str):
        try:
            return 200, {}
        except OrderNotFound as e:
            return 404, {"message": str(e)}
        except Exception:
            return 500, {}


@api.exception_handler(OrderNotFound)
def on_error(request, exc):
    return None
