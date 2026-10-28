from __future__ import annotations

from .book_room_frame import BookRoomFrame


class RoomHold:
    def __init__(self, frame: BookRoomFrame) -> None:
        self._frame: BookRoomFrame = frame

    def run(self, room_id: int, frame: BookRoomFrame) -> None:
        frame.record_done(room_id)
