from dataclasses import dataclass


@dataclass(frozen=True)
class ReadCardsResponse:
    code: str
    reading: str
