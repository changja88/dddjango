from dataclasses import dataclass


@dataclass(frozen=True)
class RenewPlanQuery:
    target_id: int
