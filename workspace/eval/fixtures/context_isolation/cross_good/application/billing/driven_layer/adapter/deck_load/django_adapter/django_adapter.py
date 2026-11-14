from __future__ import annotations

from application.billing.application_layer.port.deck_load.deck_load_port import DeckLoadPort
from application.billing.driven_layer.django_billing.models.deck_model import DeckModel


class DjangoDeckLoadAdapter(DeckLoadPort):
    def load_deck(self, rows: tuple[str, ...]) -> int:
        loaded: int = 0
        for row in rows:
            DeckModel.objects.create(body=row)
            loaded += 1
        return loaded
