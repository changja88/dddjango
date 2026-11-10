from __future__ import annotations


class Follow:
    def __init__(self, follower_id: str, followee_id: str) -> None:
        self.follower_id: str = follower_id
        self.followee_id: str = followee_id
        self._state: str = "requested"

    def accept(self) -> None:
        self._state = "mutual"
        self._ensure_valid()

    def _ensure_valid(self) -> None:
        return None
