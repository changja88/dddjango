from dataclasses import dataclass


@dataclass(frozen=True)
class RenewPlanResult:
    target_id: int
    done: bool
