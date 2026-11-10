from __future__ import annotations


class OrderRejected(Exception):
    def __init__(self, category: str) -> None:
        super().__init__(category)
        self.category: str = category
