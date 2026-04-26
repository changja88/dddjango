from rest_framework import serializers

from .models import Course


class CourseRankingSerializer(serializers.ModelSerializer):
    rank = serializers.IntegerField(read_only=True)
    instructor_name = serializers.CharField(
        source="instructor.name", read_only=True
    )
    enrollment_count = serializers.IntegerField(read_only=True)
    avg_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Course
        fields = [
            "rank",
            "id",
            "title",
            "instructor_name",
            "enrollment_count",
            "avg_rating",
        ]
