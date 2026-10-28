from dataclasses import dataclass


@dataclass(frozen=True)
class BookRoomQuery:
    target_id: int
