from __future__ import annotations

from framework.pure.text_shape import nonempty as any


def check(numbers: list[int]) -> bool:
    return any(numbers)
