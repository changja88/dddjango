from __future__ import annotations

from .grant_badge_frame import GrantBadgeFrame


class BadgeGrant:
    def __init__(self, frame: GrantBadgeFrame) -> None:
        self._frame: GrantBadgeFrame = frame

    def _run(self, member_id: int) -> None:
        assert member_id > 0
