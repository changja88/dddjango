"""서비스."""
from application.orbit.domain_layer.star_chart.value_object.zodiac.zodiac_a import ZodiacA


def resolve_star_a(x: str) -> ZodiacA:
    return ZodiacA(x)
