from __future__ import annotations

from typing import Protocol

from .split_bill_frame import SplitBillFrame


class _BillOwner(Protocol):
    def recount_bill(self, bill_id: int) -> None: ...


class BillShare:
    def __init__(self, owner: _BillOwner, frame: SplitBillFrame) -> None:
        self._owner: _BillOwner = owner
        self._frame: SplitBillFrame = frame

    def share(self, bill_id: int) -> None:
        self._owner.recount_bill(bill_id)
        self._frame.record_done(bill_id)
