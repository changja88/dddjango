"""work_shift 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class WorkShift:
    value: str
