"""#33 부칙(2026-08-25) 경계 — #335 자리(`models/<entity>_model.py`)의 첫 토큰은 면제.

entity=event_stream 의 첫 토큰 `event` 는 트리 폴더명과 겹치지만 #335 준수의 합법 귀결이다
(kkebi billing `EventStreamModel` 실물 판형).
"""


class EventStreamModel:
    id: int
    sequence: int
