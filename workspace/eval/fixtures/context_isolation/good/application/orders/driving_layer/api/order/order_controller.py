from ninja_extra import api_controller
from application.orders.domain_layer.order.value_object.money import Money
from application.orders.domain_layer.order.exception.out_of_stock import OutOfStock


@api_controller("/orders", auto_import=False)
class OrderController: ...
