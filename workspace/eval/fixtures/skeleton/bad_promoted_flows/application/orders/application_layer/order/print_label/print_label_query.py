from dataclasses import dataclass


@dataclass(frozen=True)
class PrintLabelQuery:
    target_id: int
