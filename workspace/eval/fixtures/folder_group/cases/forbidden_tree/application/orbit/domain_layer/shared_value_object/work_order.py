"""work_order 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class WorkOrder:
    value: str
