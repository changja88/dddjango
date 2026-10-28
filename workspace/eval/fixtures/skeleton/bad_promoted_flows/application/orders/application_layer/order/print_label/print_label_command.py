from dataclasses import dataclass


@dataclass(frozen=True)
class PrintLabelCommand:
    target_id: int
