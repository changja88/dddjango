"""호출 클래스 — ③."""
from ..shared_value_object.relation_gate import RelationGate


class GhostJudge:
    def __call__(self) -> RelationGate:
        raise NotImplementedError
