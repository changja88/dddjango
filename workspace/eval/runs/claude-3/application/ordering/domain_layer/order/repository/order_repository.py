"""OrderRepository — 주문 영속화 포트 (명세 §4.2 명명).

도메인이 의존하는 DIP 포트(ABC)다. 구현은 infra_layer 의 DjangoOrderRepository.
"""
from abc import ABC, abstractmethod

from application.ordering.domain_layer.order.order import Order


class OrderRepository(ABC):
    @abstractmethod
    def add(self, order: Order) -> Order:
        """주문을 영속화하고, DB 가 부여한 식별자가 채워진 Order 를 돌려준다."""
        raise NotImplementedError
