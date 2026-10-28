from dataclasses import dataclass


@dataclass(frozen=True)
class RateSellerResult:
    target_id: int
    done: bool
