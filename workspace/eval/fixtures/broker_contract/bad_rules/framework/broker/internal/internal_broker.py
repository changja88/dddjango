from __future__ import annotations

import redis
from collections import defaultdict
from collections.abc import Callable
from importlib import import_module

from framework.broker.internal.internal_broker_port import InternalBrokerPort

table = {}


class InternalBroker(InternalBrokerPort):
    def __init__(self) -> None:
        self._table = defaultdict(list)

    def subscribe(self, fact_name: str, listener_path: str) -> None:
        module = import_module(listener_path)
        self._table[fact_name].append(module)

    def publish(self, fact_name: str, order_payload: object) -> None:
        for listener in self._table[fact_name]:
            try:
                listener(order_payload)
            except Exception:
                pass
