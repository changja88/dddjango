from __future__ import annotations

from .issue_refund_frame import IssueRefundFrame
from .refund_memory import _RefundMemory, _refund_label


class CardRefund:
    def __init__(self, frame: IssueRefundFrame) -> None:
        self._frame: IssueRefundFrame = frame

    def run(self, memory: _RefundMemory) -> None:
        if _refund_label(memory):
            self._frame.record_refund(memory)
