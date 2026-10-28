from __future__ import annotations

from typing import Protocol


class _PlanOwner(Protocol):
    def charge_again(self, plan_id: int) -> None: ...


def renew_by_bank(owner: _PlanOwner, plan_id: int) -> None:
    owner.charge_again(plan_id)
