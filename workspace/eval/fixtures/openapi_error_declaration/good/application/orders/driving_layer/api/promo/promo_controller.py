from ninja import Router, Schema

router = Router()


class PromoOut(Schema):
    promo_id: str


@router.get(
    "/promos/{promo_id}",
    response={200: PromoOut},
    openapi_extra={
        "responses": {
            200: {
                "headers": {
                    "Cache-Control": {"schema": {"type": "string"}},
                    "Vary": {"schema": {"type": "string"}},
                }
            }
        }
    },
)
def get_promo(request, promo_id: str):
    return PromoOut(promo_id=promo_id)
