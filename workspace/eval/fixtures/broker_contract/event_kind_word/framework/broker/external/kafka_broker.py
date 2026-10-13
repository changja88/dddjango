from __future__ import annotations

from framework.broker.external.external_broker_port import ExternalBrokerPort, FactEnvelope


class KafkaBroker(ExternalBrokerPort):
    def publish(self, envelope: FactEnvelope) -> None:
        self._producer.send(envelope.source, envelope.body)
