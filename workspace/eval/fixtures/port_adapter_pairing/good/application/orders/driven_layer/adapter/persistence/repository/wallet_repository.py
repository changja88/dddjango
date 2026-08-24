from __future__ import annotations

from application.orders.domain_layer.wallet.exception.wallet_conflict_error import WalletConflictError
from application.orders.domain_layer.wallet.wallet_repository import WalletRepository


class DjangoWalletRepository(WalletRepository):
    def get(self, wallet_id: str) -> object:
        return None

    def save(self, wallet: object) -> None:
        target = wallet
        if target.has_pending_events:
            raise UnpulledWalletEvents()  # noqa: F821
        try:
            WalletModel.objects.filter(pk=wallet.wallet_id).update()  # noqa: F821
        except WalletConflictError:
            _observe_conflict()  # noqa: F821
            raise

