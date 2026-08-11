from pydantic import Field
from application.orders.domain_layer.order.order import Order

limit = Field(gt=0)
