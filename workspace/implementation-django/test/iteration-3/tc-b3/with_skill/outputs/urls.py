from django.urls import path

from .views import CourseRankingAPIView

app_name = "courses"

urlpatterns = [
    path(
        "api/courses/ranking/",
        CourseRankingAPIView.as_view(),
        name="course-ranking",
    ),
]
