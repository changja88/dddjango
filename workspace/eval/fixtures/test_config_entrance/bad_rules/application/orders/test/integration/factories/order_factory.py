import factory


class OrderModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "orders.OrderModel"
