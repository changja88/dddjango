from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from .models import Course
from .serializers import CourseRankingSerializer

RANKING_CACHE_TIMEOUT = 60 * 15  # 15 minutes


class CourseRankingListView(ListAPIView):
    """
    Popular course ranking API.

    Returns the top 100 courses ranked by enrollment count.
    Results are cached for 15 minutes.
    Each entry includes average rating, enrollment count, and instructor name.
    """

    serializer_class = CourseRankingSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    @method_decorator(cache_page(RANKING_CACHE_TIMEOUT))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return Course.objects.top_ranked(limit=100)

    def get_serializer(self, *args, **kwargs):
        """Inject 1-based rank into each course instance."""
        instance = args[0] if args else kwargs.get("instance")
        if instance is not None and kwargs.get("many", False):
            for idx, course in enumerate(instance, start=1):
                course.rank = idx
        return super().get_serializer(*args, **kwargs)
