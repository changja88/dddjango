from dataclasses import dataclass


@dataclass
class _RefundMemory:
    refund_id: int
    sent: bool = False


def _refund_label(memory: _RefundMemory) -> str:
    return f"refund-{memory.refund_id}"
