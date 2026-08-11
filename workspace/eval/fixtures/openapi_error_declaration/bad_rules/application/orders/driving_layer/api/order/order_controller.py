from ninja import Router, Schema

router = Router()


class OrderOut(Schema):
    order_id: str


@router.get(
    "/orders/{order_id}",
    response={200: OrderOut},
    openapi_extra={"responses": {"404": {"description": "not found"}}},
)
def get_order(request, order_id: str):
    return OrderOut(order_id=order_id)


def get_openapi_schema(api):
    return {}


router.openapi_schema = {}
