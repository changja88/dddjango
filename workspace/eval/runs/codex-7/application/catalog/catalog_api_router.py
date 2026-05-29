from ninja import NinjaAPI

from application.catalog.presentation_layer.api.reserve_stock.api_product_stock_reservations import (
    router as product_stock_reservations_router,
)

catalog_api = NinjaAPI(
    title="Catalog API",
    version="1.0.0",
    urls_namespace="catalog_api",
)
catalog_api.add_router("/catalog", product_stock_reservations_router)
