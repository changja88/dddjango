from django.db.models import QuerySet

from application.orders.driven_layer.django_orders.models.order_model import OrderModel


class DjangoOrderSummaryQuery:
    def fetch_all(self) -> "QuerySet[OrderModel]":
        return OrderModel.objects.all()

    def fetch_one(self, order_id: str) -> OrderModel:
        return OrderModel.objects.get(pk=order_id)
