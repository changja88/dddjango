from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .selectors import course_ranking_top
from .serializers import CourseRankingSerializer


class CourseRankingAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        rankings = course_ranking_top()

        for index, course in enumerate(rankings, start=1):
            course.rank = index

        serializer = CourseRankingSerializer(rankings, many=True)
        return Response(
            {"count": len(rankings), "results": serializer.data},
            status=status.HTTP_200_OK,
        )
