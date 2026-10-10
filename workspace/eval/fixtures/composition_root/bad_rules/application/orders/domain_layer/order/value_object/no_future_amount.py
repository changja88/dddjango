from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NoFutureAmount:
    value: int
