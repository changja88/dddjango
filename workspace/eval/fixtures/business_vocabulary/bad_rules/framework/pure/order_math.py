from __future__ import annotations

import random

from framework.email.email_port import EmailPort


def order_weight(order_total: int) -> int:
    return order_total + random.randint(0, 1)
