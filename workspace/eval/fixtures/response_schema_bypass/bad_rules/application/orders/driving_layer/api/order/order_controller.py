from django.http import JsonResponse
from ninja import Router, Schema

router = Router()


class OrderOut(Schema):
    order_id: str


@router.get("/orders/{order_id}", response={200: OrderOut})
def get_order(request, order_id: str):
    return JsonResponse({"order_id": order_id})
