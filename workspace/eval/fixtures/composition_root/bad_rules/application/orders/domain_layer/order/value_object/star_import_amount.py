from __future__ import annotations

from dataclasses import dataclass
from decimal import *


@dataclass(frozen=True, slots=True)
class StarImportAmount:
    value: int
