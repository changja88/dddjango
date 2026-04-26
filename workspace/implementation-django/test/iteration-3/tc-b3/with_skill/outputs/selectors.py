from django.core.cache import cache

from .models import Course

COURSE_RANKING_CACHE_KEY = "course_ranking:top100:v1"
COURSE_RANKING_CACHE_TIMEOUT = 60 * 15  # 15 minutes


def course_ranking_top(*, limit: int = 100) -> list:
    """Return top courses ranked by enrollment count with 15-minute caching."""
    cache_key = COURSE_RANKING_CACHE_KEY
    rankings = cache.get(cache_key)

    if rankings is None:
        rankings = list(Course.objects.top_ranked(limit=limit))
        cache.set(cache_key, rankings, timeout=COURSE_RANKING_CACHE_TIMEOUT)

    return rankings
