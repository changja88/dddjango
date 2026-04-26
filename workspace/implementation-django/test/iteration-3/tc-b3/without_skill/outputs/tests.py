from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from .models import Course, Enrollment, Instructor, Review


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
)
class CourseRankingAPITest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.instructor_a = Instructor.objects.create(name="Alice Kim")
        cls.instructor_b = Instructor.objects.create(name="Bob Park")

        cls.course_a = Course.objects.create(
            title="Django Masterclass",
            instructor=cls.instructor_a,
            status=Course.Status.PUBLISHED,
        )
        cls.course_b = Course.objects.create(
            title="Python Basics",
            instructor=cls.instructor_b,
            status=Course.Status.PUBLISHED,
        )
        cls.course_draft = Course.objects.create(
            title="Unpublished Course",
            instructor=cls.instructor_a,
            status=Course.Status.DRAFT,
        )

        # course_a: 3 enrollments
        for i in range(3):
            Enrollment.objects.create(
                student_name=f"student_{i}", course=cls.course_a
            )

        # course_b: 1 enrollment
        Enrollment.objects.create(
            student_name="student_0", course=cls.course_b
        )

        # course_a: reviews (avg = 4.0)
        Review.objects.create(
            course=cls.course_a, reviewer_name="r1", rating=5
        )
        Review.objects.create(
            course=cls.course_a, reviewer_name="r2", rating=3
        )

        # course_b: review (avg = 5.0)
        Review.objects.create(
            course=cls.course_b, reviewer_name="r1", rating=5
        )

    def setUp(self):
        self.client = APIClient()

    def test_ranking_returns_200(self):
        response = self.client.get("/api/courses/rankings/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ranking_ordered_by_enrollment_count_desc(self):
        response = self.client.get("/api/courses/rankings/")
        data = response.data

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["title"], "Django Masterclass")
        self.assertEqual(data[1]["title"], "Python Basics")
        self.assertGreater(
            data[0]["enrollment_count"], data[1]["enrollment_count"]
        )

    def test_ranking_includes_required_fields(self):
        response = self.client.get("/api/courses/rankings/")
        first = response.data[0]

        self.assertIn("rank", first)
        self.assertIn("title", first)
        self.assertIn("instructor_name", first)
        self.assertIn("enrollment_count", first)
        self.assertIn("avg_rating", first)

    def test_ranking_has_correct_rank_numbers(self):
        response = self.client.get("/api/courses/rankings/")
        data = response.data

        self.assertEqual(data[0]["rank"], 1)
        self.assertEqual(data[1]["rank"], 2)

    def test_ranking_instructor_name_populated(self):
        response = self.client.get("/api/courses/rankings/")
        data = response.data

        self.assertEqual(data[0]["instructor_name"], "Alice Kim")
        self.assertEqual(data[1]["instructor_name"], "Bob Park")

    def test_ranking_enrollment_count_correct(self):
        response = self.client.get("/api/courses/rankings/")
        data = response.data

        self.assertEqual(data[0]["enrollment_count"], 3)
        self.assertEqual(data[1]["enrollment_count"], 1)

    def test_ranking_avg_rating_correct(self):
        response = self.client.get("/api/courses/rankings/")
        data = response.data

        self.assertAlmostEqual(data[0]["avg_rating"], 4.0)
        self.assertAlmostEqual(data[1]["avg_rating"], 5.0)

    def test_ranking_excludes_draft_courses(self):
        response = self.client.get("/api/courses/rankings/")
        titles = [item["title"] for item in response.data]

        self.assertNotIn("Unpublished Course", titles)

    def test_ranking_excludes_archived_courses(self):
        Course.objects.create(
            title="Archived Course",
            instructor=self.instructor_a,
            status=Course.Status.ARCHIVED,
        )
        response = self.client.get("/api/courses/rankings/")
        titles = [item["title"] for item in response.data]

        self.assertNotIn("Archived Course", titles)

    def test_ranking_limited_to_top_100(self):
        """Verify the queryset caps results at 100 entries."""
        instructor = Instructor.objects.create(name="Bulk Instructor")
        courses = Course.objects.bulk_create(
            [
                Course(
                    title=f"Course {i}",
                    instructor=instructor,
                    status=Course.Status.PUBLISHED,
                )
                for i in range(110)
            ]
        )
        for course in courses:
            Enrollment.objects.create(
                student_name="student_bulk", course=course
            )

        response = self.client.get("/api/courses/rankings/")
        self.assertLessEqual(len(response.data), 100)

    def test_ranking_course_with_no_reviews_has_null_avg(self):
        course = Course.objects.create(
            title="No Review Course",
            instructor=self.instructor_a,
            status=Course.Status.PUBLISHED,
        )
        Enrollment.objects.create(
            student_name="student_x", course=course
        )

        response = self.client.get("/api/courses/rankings/")
        no_review = next(
            item for item in response.data
            if item["title"] == "No Review Course"
        )
        self.assertIsNone(no_review["avg_rating"])

    def test_ranking_query_count(self):
        """
        Ensure the ranking API executes a fixed number of queries
        regardless of the number of courses, thanks to select_related
        and annotation-based aggregation.
        """
        with self.assertNumQueries(1):
            self.client.get("/api/courses/rankings/")

    def test_ranking_allows_unauthenticated_access(self):
        """Ranking is a public endpoint - no auth required."""
        client = APIClient()
        response = client.get("/api/courses/rankings/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
