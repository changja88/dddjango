from __future__ import annotations


class _CountOrderFailure(Exception):
    def __init__(self, category: str) -> None:
        super().__init__(category)
        self.category: str = category
