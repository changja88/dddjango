from __future__ import annotations

from framework.smtp_client.smtp_client_port import SmtpClientPort


class KafkaAdapter(SmtpClientPort):
    def push(self, body: str) -> None:
        return None
