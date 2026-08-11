from abc import ABC, abstractmethod
from django.db.models import QuerySet


class PaymentGatewayPort(ABC):
    @abstractmethod
    def charge(self, command) -> QuerySet: ...
