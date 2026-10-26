"""rank_link_table 서비스."""
from typing import Dict
from application.orbit.domain_layer.shared_value_object.moon_phase import MoonPhase
from application.orbit.domain_layer.shared_value_object.relation_link import RelationLink


def rank_link_table() -> Dict[MoonPhase, RelationLink]:
    raise NotImplementedError
