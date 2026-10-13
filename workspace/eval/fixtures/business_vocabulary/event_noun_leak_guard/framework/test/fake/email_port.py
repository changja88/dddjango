from __future__ import annotations

from framework.email.email_port import EmailPort


class FakeEmail(EmailPort):
    def send(self, notice: object, event_name: str, booked_code: str) -> None:
        return None
