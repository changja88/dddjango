"""work_load 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class WorkLoad:
    value: str
