import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from application.inventory.application_layer.reserve_stock.command.reserve_stock_app import (
    ReserveStockApp,
)
from application.inventory.domain_layer.product.exceptions import InsufficientStock


@require_POST
def reserve_view(request, product_id: int) -> JsonResponse:
    body = json.loads(request.body or b"{}")
    quantity = int(body.get("quantity", 0))
    try:
        ReserveStockApp().execute(product_id, quantity)
    except InsufficientStock:
        return JsonResponse({"error": "insufficient stock"}, status=409)
    return JsonResponse({"status": "ok"}, status=200)
