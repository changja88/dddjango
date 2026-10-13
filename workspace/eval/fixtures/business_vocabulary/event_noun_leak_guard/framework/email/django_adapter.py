from __future__ import annotations

from framework.email.email_port import EmailPort
from framework.email.notice_out import NoticeOut


class DjangoEmailAdapter(EmailPort):
    def send(self, notice: NoticeOut, event_name: str, booked_code: str) -> None:
        return None
