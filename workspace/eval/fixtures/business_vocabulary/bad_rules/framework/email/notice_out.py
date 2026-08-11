from __future__ import annotations

from dataclasses import dataclass
from django.utils.translation import gettext


@dataclass(frozen=True)
class NoticeOut:
    api_key: str
    order_label: str


@dataclass(frozen=True)
class TinyOut:
    code: str
