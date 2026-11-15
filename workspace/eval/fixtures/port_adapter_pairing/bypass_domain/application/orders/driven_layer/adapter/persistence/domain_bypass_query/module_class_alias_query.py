from application.orders.driven_layer.django_orders.models import order_model as m


class DjangoModuleClassAliasDomainBypassQuery:
    def count(self) -> int:
        return m.OrderModel.objects.filter(status=m.OrderModel.Status.PENDING).count()
