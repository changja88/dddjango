from dataclasses import dataclass


@dataclass(frozen=True)
class PrintLabelResult:
    target_id: int
    done: bool
