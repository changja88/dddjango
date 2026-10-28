from dataclasses import dataclass


@dataclass(frozen=True)
class RenewPlanCommand:
    target_id: int
