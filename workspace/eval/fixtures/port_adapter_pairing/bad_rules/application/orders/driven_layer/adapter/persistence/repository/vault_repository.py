from __future__ import annotations

from application.orders.domain_layer.vault.vault_repository import VaultRepository


class DjangoVaultRepository(VaultRepository):
    def get(self, vault_id: str) -> object:
        return None

    def save(self, vault: object) -> None:
        if vault.is_archived:
            raise ArchivedVault()  # noqa: F821
        VaultModel.objects.filter(pk=vault.vault_id).update()  # noqa: F821

