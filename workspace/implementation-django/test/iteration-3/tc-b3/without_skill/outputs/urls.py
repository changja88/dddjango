from django.urls import path

from .views import CourseRankingListView

urlpatterns = [
    path(
        "rankings/",
        CourseRankingListView.as_view(),
        name="course-ranking-list",
    ),
]
