from application.orders.driven_layer.django_orders.models.star_seed_model import OrderStatus, StarSeedModel


class DjangoStarSeedDomainBypassQuery:
    def count(self) -> int:
        return StarSeedModel.objects.filter(status__in=[StarSeedModel.Status.PENDING, OrderStatus.SHIPPED]).count()
