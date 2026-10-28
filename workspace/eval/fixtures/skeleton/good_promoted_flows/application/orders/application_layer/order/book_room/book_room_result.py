from dataclasses import dataclass


@dataclass(frozen=True)
class BookRoomResult:
    target_id: int
    done: bool
