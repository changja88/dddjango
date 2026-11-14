from __future__ import annotations

from application.billing.application_layer.port.ledger_load.ledger_load_port import LedgerLoadPort
from application.billing.driven_layer.django_billing.models.ledger_model import LedgerModel


class DjangoLedgerLoadAdapter(LedgerLoadPort):
    def load_rows(self, batch: tuple[str, ...]) -> int:
        created: int = 0
        for row in batch:
            LedgerModel.objects.create(body=row)
            created += 1
        return created
