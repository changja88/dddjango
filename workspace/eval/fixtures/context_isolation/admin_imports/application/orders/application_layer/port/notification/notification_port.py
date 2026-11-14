from abc import ABC, abstractmethod


class NotificationPort(ABC):
    @abstractmethod
    def send(self, payload_id: str) -> None: ...
