from abc import ABC, abstractmethod


class InvoiceLookupPort(ABC):
    @abstractmethod
    def fetch(self, invoice_id: str) -> str: ...
