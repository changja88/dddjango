from application.orders.domain_layer.order.exception import OrderRejected
from application.orders.domain_layer.order.value_object.order_kind import OrderKind

_ORDER_KINDS: tuple[str, ...] = tuple(member.value for member in OrderKind)
_REJECTED_NAME: str = OrderRejected.__name__
