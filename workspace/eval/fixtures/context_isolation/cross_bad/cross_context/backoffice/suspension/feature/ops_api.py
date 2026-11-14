from ninja import Router

router: Router = Router()


@router.get("/orders")
def orders(request: object) -> list[str]:
    return []
