from config.api import api
from application.orders.driving_layer.api.api_router import register_orders_api

register_orders_api(api)

urlpatterns: list = []
