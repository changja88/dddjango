from application.catalog.application_layer.reserve_product_stock.command.reserve_product_stock_app import (
    ReserveProductStockResult,
)


def reserve_product_stock_response(result: ReserveProductStockResult) -> dict[str, int]:
    return {
        "product_id": result.product_id,
        "stock": result.stock,
    }
