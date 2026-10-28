from dataclasses import dataclass


@dataclass(frozen=True)
class RateSellerCommand:
    target_id: int
