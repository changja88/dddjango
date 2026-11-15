from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class RefundRule:
    days: int

    def allows(self, elapsed: int) -> bool:
        return elapsed <= self.days


class RefundPlan(Enum):
    STANDARD = RefundRule(7)
