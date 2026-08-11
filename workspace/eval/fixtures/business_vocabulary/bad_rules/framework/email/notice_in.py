from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NoticeIn:
    order_receipt: "Order"  # noqa: F821
