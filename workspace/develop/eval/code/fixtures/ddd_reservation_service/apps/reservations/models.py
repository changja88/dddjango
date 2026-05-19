from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class ReservationStatus(str, Enum):
    DRAFT = "draft"
    REQUESTED = "requested"
    CONFIRMED = "confirmed"
    EXPIRED = "expired"


@dataclass
class Reservation:
    customer_id: str
    room_id: str
    nights: int
    id: str = field(default_factory=lambda: str(uuid4()))
    status: ReservationStatus = ReservationStatus.DRAFT
