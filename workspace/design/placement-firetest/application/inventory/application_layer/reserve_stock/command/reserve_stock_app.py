from application.inventory.infra_layer.django_inventory.models.product_model import (
    ProductModel,
)


class ReserveStockApp:
    def execute(self, product_id: int, quantity: int) -> None:
        product = ProductModel.objects.get(pk=product_id)
        product.reserve(quantity)
