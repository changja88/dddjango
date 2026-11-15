from application.orders.driven_layer.django_orders import models as mm


class DjangoPackageModuleClassDomainBypassQuery:
    def count(self) -> int:
        return mm.OrderModel.objects.filter(status=mm.OrderModel.Status.PENDING).count()
