"""OrderRepository — Order 영속화 추상화(ABC).

도메인이 의존하는 안정적 역할(포트). 구현은 인프라(DjangoOrderRepository)가 제공한다.
"""
from abc import ABC, abstractmethod

from application.catalog.domain_layer.order.order import Order


class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> int:
        """Order를 영속화하고 부여된 PK(id)를 반환한다."""
        raise NotImplementedError
