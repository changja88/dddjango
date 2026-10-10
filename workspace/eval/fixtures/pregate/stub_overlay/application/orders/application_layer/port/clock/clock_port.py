"""시계 포트 — pre-gate 스텁 픽스처의 어댑터가 구현하는 계약."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime


class ClockPort(ABC):
    @abstractmethod
    def now(self) -> datetime: ...
