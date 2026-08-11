from __future__ import annotations

from application.orders.driven_layer.persistence.repository.django_order_repository import DjangoOrderRepository
from framework.email.smtp_adapter import SmtpAdapter


class NotifyUseCase:
    def execute(self, order_id: str) -> None:
        return None
