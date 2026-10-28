from dataclasses import dataclass


@dataclass(frozen=True)
class BookRoomCommand:
    target_id: int
