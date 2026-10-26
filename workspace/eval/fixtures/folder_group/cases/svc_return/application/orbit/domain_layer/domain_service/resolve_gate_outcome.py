"""resolve_gate_outcome 서비스."""
from typing import Union
from ..shared_value_object.relation_gate import RelationGate
from ..shared_value_object.moon_missing import MoonMissing


def resolve_gate_outcome() -> Union[RelationGate, MoonMissing]:
    raise NotImplementedError
