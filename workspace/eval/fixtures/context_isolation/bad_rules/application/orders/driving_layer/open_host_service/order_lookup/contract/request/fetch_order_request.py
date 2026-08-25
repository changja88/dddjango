from dataclasses import dataclass

type UnusedAlias = StrayNote


@dataclass(frozen=True)
class StrayNote:
    text: str


@dataclass(frozen=True)
class FetchOrderRequest:
    order_id: str
