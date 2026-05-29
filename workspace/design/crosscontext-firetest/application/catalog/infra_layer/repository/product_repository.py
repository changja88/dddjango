from application.catalog.domain_layer.product.product import Product


class ProductRepository:
    def get(self, product_id: int) -> Product:
        raise NotImplementedError

    def save(self, product: Product) -> None:
        raise NotImplementedError
