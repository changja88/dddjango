import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from application.inventory.application_layer.deduct_stock.command.deduct_stock_app import (
    DeductStockApp,
)
from application.inventory.domain_layer.product.exceptions import InsufficientStock
from application.inventory.infra_layer.repository.product_repository import (
    ProductRepository,
)


@require_POST
def deduct_stock_view(request, product_id: int) -> JsonResponse:
    body = json.loads(request.body or b"{}")
    quantity = int(body.get("quantity", 0))
    app = DeductStockApp(ProductRepository())
    try:
        app.execute(product_id, quantity)
    except InsufficientStock:
        return JsonResponse({"error": "insufficient stock"}, status=409)
    return JsonResponse({"status": "ok"}, status=200)
