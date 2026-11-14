from application.orders.driven_layer.django_orders.models import order_model
from application.orders.driven_layer.django_orders.models.order_model import OrderModel
from application.orders.driving_layer.open_host_service.order_lookup.order_lookup_service import get_order_query

ROWS: object = (OrderModel.objects.all(), order_model.OrderModel, get_order_query)
