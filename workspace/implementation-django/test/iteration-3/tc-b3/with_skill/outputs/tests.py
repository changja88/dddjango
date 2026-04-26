from django.core.cache import cache
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .factories import CourseFactory, EnrollmentFactory, InstructorFactory, ReviewFactory
from .models import Course
from .selectors import COURSE_RANKING_CACHE_KEY, course_ranking_top


class CourseRankingQuerySetTest(TestCase):
    def setUp(self):
        self.instructor = InstructorFactory()
        self.courses = CourseFactory.create_batch(
            5, published=True, instructor=self.instructor
        )
        for i, course in enumerate(self.courses):
            EnrollmentFactory.create_batch(
                (i + 1) * 10, course=course
            )
            ReviewFactory.create_batch(3, course=course)

    def test_top_ranked_orders_by_enrollment_count_descending(self):
        """top_ranked() returns courses ordered by enrollment count descending."""
        ranked = list(Course.objects.top_ranked())
        enrollment_counts = [c.enrollment_count for c in ranked]
        self.assertEqual(enrollment_counts, sorted(enrollment_counts, reverse=True))

    def test_top_ranked_includes_annotations(self):
        """top_ranked() annotates enrollment_count and avg_rating."""
        ranked = list(Course.objects.top_ranked())
        first = ranked[0]
        self.assertIsNotNone(first.enrollment_count)
        self.assertIsNotNone(first.avg_rating)
        self.assertTrue(first.enrollment_count > 0)

    def test_top_ranked_excludes_non_published_courses(self):
        """top_ranked() excludes draft and archived courses."""
        CourseFactory(status=Course.Status.DRAFT, instructor=self.instructor)
        CourseFactory(status=Course.Status.ARCHIVED, instructor=self.instructor)
        ranked = list(Course.objects.top_ranked())
        statuses = {c.status for c in ranked}
        self.assertEqual(statuses, {Course.Status.PUBLISHED})

    def test_top_ranked_respects_limit(self):
        """top_ranked() respects the limit parameter."""
        ranked = list(Course.objects.top_ranked(limit=3))
        self.assertEqual(len(ranked), 3)

    def test_top_ranked_query_count(self):
        """top_ranked() executes in a constant number of queries."""
        with self.assertNumQueries(1):
            list(Course.objects.top_ranked())

    def test_top_ranked_includes_instructor_via_select_related(self):
        """Accessing instructor.name causes no additional query."""
        ranked = list(Course.objects.top_ranked())
        with self.assertNumQueries(0):
            for course in ranked:
                _ = course.instructor.name


class CourseRankingSelectorTest(TestCase):
    def setUp(self):
        cache.clear()
        instructor = InstructorFactory()
        self.courses = CourseFactory.create_batch(
            3, published=True, instructor=instructor
        )
        for i, course in enumerate(self.courses):
            EnrollmentFactory.create_batch((i + 1) * 5, course=course)

    def tearDown(self):
        cache.clear()

    def test_course_ranking_top_returns_list(self):
        """course_ranking_top() returns a list of courses."""
        result = course_ranking_top()
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)

    def test_course_ranking_top_caches_result(self):
        """Second call to course_ranking_top() uses cache (0 queries)."""
        course_ranking_top()
        with self.assertNumQueries(0):
            course_ranking_top()

    def test_course_ranking_top_cache_invalidation(self):
        """Clearing cache causes fresh query on next call."""
        course_ranking_top()
        cache.delete(COURSE_RANKING_CACHE_KEY)
        with self.assertNumQueries(1):
            course_ranking_top()


class CourseRankingAPITest(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        instructor = InstructorFactory()
        self.courses = CourseFactory.create_batch(
            5, published=True, instructor=instructor
        )
        for i, course in enumerate(self.courses):
            EnrollmentFactory.create_batch((i + 1) * 10, course=course)
            ReviewFactory.create_batch(2, course=course)

    def tearDown(self):
        cache.clear()

    def test_ranking_api_returns_200(self):
        """GET /api/courses/ranking/ returns HTTP 200."""
        response = self.client.get("/api/courses/ranking/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ranking_api_response_structure(self):
        """Response contains count and results with expected fields."""
        response = self.client.get("/api/courses/ranking/")
        data = response.json()
        self.assertIn("count", data)
        self.assertIn("results", data)
        self.assertEqual(data["count"], 5)

        first = data["results"][0]
        self.assertIn("rank", first)
        self.assertIn("id", first)
        self.assertIn("title", first)
        self.assertIn("instructor_name", first)
        self.assertIn("enrollment_count", first)
        self.assertIn("avg_rating", first)

    def test_ranking_api_order(self):
        """Results are ordered by enrollment_count descending."""
        response = self.client.get("/api/courses/ranking/")
        results = response.json()["results"]
        enrollment_counts = [r["enrollment_count"] for r in results]
        self.assertEqual(enrollment_counts, sorted(enrollment_counts, reverse=True))

    def test_ranking_api_rank_numbering(self):
        """Rank numbers are sequential starting from 1."""
        response = self.client.get("/api/courses/ranking/")
        results = response.json()["results"]
        ranks = [r["rank"] for r in results]
        self.assertEqual(ranks, list(range(1, len(results) + 1)))

    def test_ranking_api_includes_instructor_name(self):
        """Each result includes the instructor's name."""
        response = self.client.get("/api/courses/ranking/")
        results = response.json()["results"]
        for result in results:
            self.assertIsNotNone(result["instructor_name"])
            self.assertTrue(len(result["instructor_name"]) > 0)

    def test_ranking_api_query_count_uncached(self):
        """Uncached ranking API call executes a bounded number of queries."""
        with self.assertNumQueries(1):
            self.client.get("/api/courses/ranking/")

    def test_ranking_api_query_count_cached(self):
        """Cached ranking API call executes zero DB queries."""
        self.client.get("/api/courses/ranking/")
        with self.assertNumQueries(0):
            self.client.get("/api/courses/ranking/")
