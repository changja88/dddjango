from dataclasses import dataclass


@dataclass(frozen=True)
class IssueRefundResult:
    target_id: int
    done: bool
