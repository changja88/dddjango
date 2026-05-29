from application.orders.application_layer.create_order.dto.create_order_command import (
    CreateOrderResult,
)


def order_created_body(result: CreateOrderResult) -> dict[str, object]:
    return {
        "id": result.id,
        "product_id": result.product_id,
        "quantity": result.quantity,
        "status": result.status,
    }
