"""서비스."""
from application.orbit.domain_layer.star_chart.value_object.zodiac.zodiac_b import ZodiacB


def resolve_star_b(x: str) -> ZodiacB:
    return ZodiacB(x)
