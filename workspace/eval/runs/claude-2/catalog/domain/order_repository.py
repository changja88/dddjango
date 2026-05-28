"""Order 리포지토리 추상화(포트).

설계 명세 section 4: Order 저장(ORM<->도메인 Data Mapper)을 인프라 구현이 소유한다.
"""

from abc import ABC, abstractmethod

from catalog.domain.order import Order


class OrderRepository(ABC):
    @abstractmethod
    def add(self, order: Order) -> Order:
        """Order를 저장하고 식별자가 채워진 Order를 반환한다."""
        raise NotImplementedError
