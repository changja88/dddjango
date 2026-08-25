from dataclasses import dataclass


@dataclass(frozen=True)
class ReadCardsRequest:
    selection: str
