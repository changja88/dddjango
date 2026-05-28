from typing import Any, Dict

from application.catalog.domain_layer.order.entity.order import Order


def order_to_response(order: Order) -> Dict[str, Any]:
    return {
        "id": order.id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "unit_price": order.unit_price,
        "created_at": order.created_at,
    }
