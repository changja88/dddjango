"""void_disk 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class VoidDisk:
    value: str
