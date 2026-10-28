from __future__ import annotations

from typing import Protocol


class _NoticeOwner(Protocol):
    def charge_again(self, plan_id: int) -> None: ...


def send_notice(plan_id: int, owner: _NoticeOwner) -> None:
    owner.charge_again(plan_id)
