"""Django 가 모델을 발견할 수 있도록 OrderModel 을 패키지 레벨에 노출한다."""
from application.ordering.infra_layer.django_ordering.models.order_model import OrderModel

__all__ = ["OrderModel"]
