from ninja import Router

router = Router()


@router.get("/orders")
def list_orders(request):
    return []
