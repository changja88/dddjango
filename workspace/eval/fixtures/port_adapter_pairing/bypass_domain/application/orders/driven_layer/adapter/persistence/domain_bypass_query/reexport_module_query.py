import application.orders.driven_layer.django_orders.models.order_model as m


class DjangoReexportModuleDomainBypassQuery:
    def count(self) -> int:
        return m.OrderModel.objects.filter(status=m.Kind.PENDING).count()
