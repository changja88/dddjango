from abc import ABC, abstractmethod
from collections.abc import Callable


class ExternalBrokerPort(ABC):
    @abstractmethod
    def subscribe(self, fact_name: str, listener: Callable[[object], None]) -> None:
        raise NotImplementedError

    @abstractmethod
    def publish(self, fact: object) -> None:
        raise NotImplementedError
