"""compose_mix 서비스."""
from application.orbit.domain_layer.shared_value_object.relation_link import RelationLink
from application.orbit.domain_layer.shared_value_object.moon_phase import MoonPhase


def compose_mix() -> tuple[RelationLink, MoonPhase]:
    raise NotImplementedError
