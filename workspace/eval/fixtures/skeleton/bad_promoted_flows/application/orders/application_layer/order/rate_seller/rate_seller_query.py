from dataclasses import dataclass


@dataclass(frozen=True)
class RateSellerQuery:
    target_id: int
