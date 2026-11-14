from typing import Any


def test_rows_start_empty() -> None:
    state: dict[str, Any] = {}
    assert state == {}
