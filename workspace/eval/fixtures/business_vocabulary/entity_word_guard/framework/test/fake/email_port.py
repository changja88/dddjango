from __future__ import annotations

from framework.email.email_port import EmailPort


class FakeEmail(EmailPort):
    def send(self, notice: object, entity_name: str) -> None:
        return None
