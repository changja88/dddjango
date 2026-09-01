from ninja import Router, Schema

router = Router()

EXTRA_RESPONSES = {"200": {"description": "ok"}}
SUCCESS_META = {"headers": {"X-Trace": {"schema": {"type": "string"}}}}


class PromoOut(Schema):
    promo_id: str


@router.get(
    "/promos/{promo_id}",
    response={200: PromoOut},
    openapi_extra={"responses": {OK_STATUS: {"description": "ok"}}},
)
def get_promo(request, promo_id: str):
    return PromoOut(promo_id=promo_id)


@router.get(
    "/promos",
    response={200: PromoOut},
    openapi_extra={"responses": {**EXTRA_RESPONSES, 200: SUCCESS_META}},
)
def list_promos(request):
    return PromoOut(promo_id="p")


@router.get(
    "/promos/featured",
    response={200: PromoOut},
    openapi_extra={"responses": {201: {"description": "created via extra only"}}},
)
def featured_promo(request):
    return PromoOut(promo_id="f")


OK_STATUS = 200
