from typing import Any


def _session_state() -> dict[str, object]:
    return {}


def test_session_state_is_empty():
    state: dict[str, Any] = _session_state()
    assert state == {}
