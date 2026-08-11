from __future__ import annotations

from framework.email.email_port import EmailPort
from framework.email.notice_out import NoticeOut


class DjangoEmailAdapter(EmailPort):
    def send(self, notice: NoticeOut) -> None:
        return None
