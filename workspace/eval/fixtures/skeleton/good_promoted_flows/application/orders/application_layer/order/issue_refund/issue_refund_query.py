from dataclasses import dataclass


@dataclass(frozen=True)
class IssueRefundQuery:
    target_id: int
