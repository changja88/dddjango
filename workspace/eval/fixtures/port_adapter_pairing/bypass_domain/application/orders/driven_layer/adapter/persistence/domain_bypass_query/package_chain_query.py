from application.orders.driven_layer.django_orders import models as mm


class DjangoPackageChainDomainBypassQuery:
    def count(self) -> int:
        return mm.order_model.OrderModel.objects.filter(status=mm.order_model.OrderModel.Status.PENDING).count()
