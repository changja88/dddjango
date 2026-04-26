from django.db import models
from django.db.models import Avg, Count
from django.db.models.functions import Now


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(db_default=Now())
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Instructor(TimeStampedModel):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class CourseQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=Course.Status.PUBLISHED)

    def with_ranking_annotations(self):
        return self.annotate(
            enrollment_count=Count("enrollments", distinct=True),
            avg_rating=Avg("reviews__rating"),
        )

    def top_ranked(self, limit=100):
        return (
            self.published()
            .with_ranking_annotations()
            .select_related("instructor")
            .order_by("-enrollment_count")[:limit]
        )


class Course(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.CASCADE,
        related_name="courses",
    )
    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.DRAFT,
        db_index=True,
    )

    objects = CourseQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["status", "-created_at"],
                name="idx_course_status_created",
            ),
        ]

    def __str__(self):
        return self.title


class Enrollment(TimeStampedModel):
    student_name = models.CharField(max_length=100)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student_name", "course"],
                name="unique_enrollment_per_student",
            ),
        ]

    def __str__(self):
        return f"{self.student_name} - {self.course.title}"


class Review(TimeStampedModel):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    reviewer_name = models.CharField(max_length=100)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(rating__gte=1, rating__lte=5),
                name="review_rating_range",
            ),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.rating is not None and not (1 <= self.rating <= 5):
            raise ValidationError(
                {"rating": "Rating must be between 1 and 5."}
            )

    def __str__(self):
        return f"{self.course.title} - {self.rating}"
