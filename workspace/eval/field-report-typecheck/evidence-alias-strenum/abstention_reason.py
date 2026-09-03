from enum import StrEnum as _StrEnum


class AbstentionReason(_StrEnum):
    """정상 근거 없음의 닫힌 이유 집합."""

    NO_CANDIDATE = "no_candidate"
    NO_EVIDENCE = "no_evidence"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
