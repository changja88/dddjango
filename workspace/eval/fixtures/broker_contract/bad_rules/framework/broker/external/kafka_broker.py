from __future__ import annotations

from framework.broker.external.external_broker_port import ExternalBrokerPort


class KafkaBroker(ExternalBrokerPort):
    def publish(self, topic: str, payload: str) -> None:
        self._producer.send(topic, payload)
