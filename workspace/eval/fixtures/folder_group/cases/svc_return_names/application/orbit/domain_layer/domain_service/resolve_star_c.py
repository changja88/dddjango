"""서비스."""
from application.orbit.domain_layer.star_chart.value_object.zodiac.zodiac_c import ZodiacC


def resolve_star_c(x: str) -> ZodiacC:
    return ZodiacC(x)
