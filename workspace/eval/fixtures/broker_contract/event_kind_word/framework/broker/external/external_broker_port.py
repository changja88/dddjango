from __future__ import annotations

from abc import ABC, abstractmethod

"""보장: at-least-once — 같은 봉투가 두 번 올 수 있다. 발행은 outbox 를 거쳐
커밋과 한 트랜잭션에 묶인다. ordering: 보장하지 않는다. serializer: json.
schema version 필드 필수. 실패는 dead_letter 로 보낸다.
"""


class FactEnvelope:
    source: str
    event_id: str
    version: str
    body: str


class ExternalBrokerPort(ABC):
    @abstractmethod
    def publish(self, envelope: FactEnvelope) -> None: ...
