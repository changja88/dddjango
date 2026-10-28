from dataclasses import dataclass


@dataclass(frozen=True)
class IssueRefundCommand:
    target_id: int
