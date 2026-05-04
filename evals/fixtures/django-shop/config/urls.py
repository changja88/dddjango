from django.urls import path

from shop.orders import views


urlpatterns = [
    path("orders/<int:order_id>/cancel/", views.cancel_order),
    path("orders/<int:order_id>/reserve/", views.reserve_inventory),
]
