from dataclasses import dataclass

type CardSelection = MajorCardSelection | MinorCardSelection
type AnyCardSelection = CardSelection


@dataclass(frozen=True)
class MajorCardSelection:
    name: str


@dataclass(frozen=True)
class MinorCardSelection:
    name: str
    suit: str


@dataclass(frozen=True)
class SelectCardsRequest:
    selection: AnyCardSelection
