import json

from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from shop.orders.models import Order, Product, Reservation


@require_POST
def cancel_order(request, order_id):
    payload = json.loads(request.body or "{}")
    order = Order.objects.get(id=order_id)
    order.cancel(
        reason=payload.get("reason", ""),
        actor_email=payload.get("actor_email", "system@example.com"),
    )
    return JsonResponse({"id": order.id, "status": order.status})


@require_POST
def reserve_inventory(request, order_id):
    payload = json.loads(request.body or "{}")
    product_id = payload["product_id"]
    quantity = int(payload["quantity"])
    idempotency_key = request.headers.get("Idempotency-Key", "")

    with transaction.atomic():
        product = Product.objects.select_for_update().get(id=product_id)
        order = Order.objects.select_for_update().get(id=order_id)
        if product.stock_quantity < quantity:
            return JsonResponse(
                {"error": "not_enough_stock", "available": product.stock_quantity},
                status=409,
            )
        product.stock_quantity -= quantity
        product.save(update_fields=["stock_quantity"])
        reservation = Reservation.objects.create(
            product=product,
            order=order,
            quantity=quantity,
            idempotency_key=idempotency_key,
        )

    return JsonResponse({"reservation_id": reservation.id}, status=201)
