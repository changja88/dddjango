from __future__ import annotations

from dataclasses import dataclass

from .shelf_count import ShelfCount


@dataclass
class CountMemory:
    shelf_id: int
    counted: bool = False
    counter: ShelfCount | None = None
