from __future__ import annotations

from framework.broker.external.external_broker_port import ExternalBrokerPort


class AnnounceUseCase:
    def execute(self, order_id: str) -> None:
        try:
            delivered = self._broker.publish("order_placed", order_id)
        except Exception:
            delivered = False
        self._acl.confirm(order_id)
