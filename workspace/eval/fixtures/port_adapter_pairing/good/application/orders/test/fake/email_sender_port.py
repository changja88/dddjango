from __future__ import annotations

from application.orders.application_layer.port.email_sender.email_sender_port import EmailSenderPort


class FakeEmailSender(EmailSenderPort):
    def send(self, notice: object) -> None:
        return None
