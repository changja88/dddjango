from __future__ import annotations

from framework.broker.internal.internal_broker import InternalBroker


def build_announce() -> object:
    broker = InternalBroker()
    return broker
