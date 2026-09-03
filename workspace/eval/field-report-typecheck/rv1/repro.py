from dataclasses import dataclass
from enum import StrEnum


@dataclass(frozen=True, slots=True)
class Money:
    amount: int
    currency: str = "KRW"

    def __post_init__(self) -> None:
        if not isinstance(self.amount, int):
            object.__setattr__(self, "amount", int(self.amount))
        if self.amount < 0:
            raise ValueError("neg")


class CallerLabel:
    @classmethod
    def create(cls, value: str) -> "CallerLabel":
        if not isinstance(value, str) or not value.strip():
            raise ValueError("bad")
        return cls()


class BookUsagePolicy(StrEnum):
    SINGLE: str = "single"
    COMPARE: str = "compare"


class Fixed(StrEnum):
    SINGLE = "single"
