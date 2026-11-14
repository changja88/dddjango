from abc import ABC, abstractmethod


class OrderLookupPort(ABC):
    @abstractmethod
    def fetch(self, order_id: str) -> str: ...
